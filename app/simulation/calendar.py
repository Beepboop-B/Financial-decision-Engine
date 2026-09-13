from typing import List, Dict, Tuple, Set
from datetime import date, timedelta
from decimal import Decimal

from app.models.state import CanonicalUserState, CanonicalEvent
from app.simulation.models import ForecastEvent, ScenarioOverlay

class UnresolvedAmountError(Exception):
    pass

def add_months(d: date, months: int) -> date:
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    day = d.day
    while True:
        try:
            return date(year, month, day)
        except ValueError:
            day -= 1

def apply_spending_changes(events: List[CanonicalEvent], overrides: List[str]) -> List[CanonicalEvent]:
    modified_events = []
    
    stop_ids = set()
    reductions = {}
    
    for override in overrides:
        parts = override.split(':')
        if parts[0] == 'stop':
            stop_ids.add(parts[1])
        elif parts[0] == 'reduce_to':
            reductions[parts[1]] = Decimal(parts[2])

    for ce in events:
        if ce.event_id in stop_ids:
            if ce.flexibility not in ('stoppable', 'reducible_or_stoppable'):
                raise ValueError(f"Cannot stop non-stoppable expense {ce.event_id}")
            continue
            
        new_ce = ce
        if ce.event_id in reductions:
            if ce.flexibility not in ('reducible', 'reducible_or_stoppable'):
                raise ValueError(f"Cannot reduce non-reducible expense {ce.event_id}")
            new_ce = CanonicalEvent(**ce.__dict__)
            new_ce.normalized_amount = reductions[ce.event_id]
            
        modified_events.append(new_ce)
        
    return modified_events

def build_event_calendar(
    canonical_user_state: CanonicalUserState,
    request_date: date,
    horizon_days: int = 90,
    overlay: ScenarioOverlay = None
) -> List[ForecastEvent]:
    
    if overlay is None:
        overlay = ScenarioOverlay()
        
    end_date = request_date + timedelta(days=horizon_days)
    
    active_events = canonical_user_state.active_events
    if overlay.spending_changes:
        active_events = apply_spending_changes(active_events, overlay.spending_changes)
        
    forecast_events = []
    
    for ce in active_events:
        if ce.is_unresolved_amount:
            raise UnresolvedAmountError(f"Event {ce.event_id} has unresolved amount.")
            
        amount = ce.normalized_amount
        direction = 'inflow' if ce.direction == 'credit' else 'outflow'
        priority = 0 if direction == 'inflow' else 1
        
        if ce.is_recurring:
            current_date = ce.anchor_date
            
            while current_date < request_date:
                if ce.frequency == 'monthly':
                    current_date = add_months(current_date, 1)
                elif ce.frequency == 'weekly':
                    current_date += timedelta(days=7)
                elif ce.frequency == 'biweekly':
                    current_date += timedelta(days=14)
                else:
                    break
                    
            while current_date <= end_date:
                if current_date >= request_date:
                    forecast_events.append(ForecastEvent(
                        date=current_date,
                        event_id=ce.event_id,
                        amount=amount,
                        direction=direction,
                        category=ce.category,
                        source_type="canonical",
                        event_type=ce.event_type,
                        priority=priority
                    ))
                    
                if ce.frequency == 'monthly':
                    current_date = add_months(current_date, 1)
                elif ce.frequency == 'weekly':
                    current_date += timedelta(days=7)
                elif ce.frequency == 'biweekly':
                    current_date += timedelta(days=14)
                else:
                    break
        else:
            if request_date <= ce.event_date <= end_date:
                forecast_events.append(ForecastEvent(
                    date=ce.event_date,
                    event_id=ce.event_id,
                    amount=amount,
                    direction=direction,
                    category=ce.category,
                    source_type="canonical",
                    event_type=ce.event_type,
                    priority=priority
                ))
                
    for payment in overlay.candidate_payments:
        if request_date <= payment.date <= end_date:
            forecast_events.append(payment)
            
    forecast_events.sort(key=lambda x: (x.date, x.priority, x.event_id))
    
    return forecast_events
