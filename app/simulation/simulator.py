from datetime import date, timedelta
from typing import List
from decimal import Decimal
from collections import defaultdict

from app.models.state import CanonicalUserState, RequestContext
from app.simulation.models import (
    ForecastEvent, ScenarioOverlay, DailyBalanceCheckpoint,
    SimulationTrace, SafetyResult, SimulationResult
)
from app.simulation.calendar import build_event_calendar

class ReferenceSimulator:
    @staticmethod
    def simulate(
        state: CanonicalUserState,
        request_context: RequestContext,
        horizon_days: int = 90,
        overlay: ScenarioOverlay = None
    ) -> SimulationResult:
        
        req_date = request_context.request_date
        end_date = req_date + timedelta(days=horizon_days)
        
        events = build_event_calendar(state, req_date, horizon_days, overlay)
        events_by_date = defaultdict(list)
        for e in events:
            events_by_date[e.date].append(e)
            
        current_balance = state.current_balance
        min_balance = current_balance
        min_date = req_date
        first_violation = None
        violation_amount = None
        
        checkpoints = []
        
        curr_date = req_date
        while curr_date <= end_date:
            balance_start = current_balance
            inflows = Decimal("0")
            outflows = Decimal("0")
            day_events = events_by_date[curr_date]
            
            for e in day_events:
                if e.direction == 'inflow':
                    inflows += e.amount
                    current_balance += e.amount
                else:
                    outflows += e.amount
                    current_balance -= e.amount
                    
            if current_balance < min_balance:
                min_balance = current_balance
                min_date = curr_date
                
            if current_balance < state.minimum_balance_to_keep and first_violation is None:
                first_violation = curr_date
                violation_amount = state.minimum_balance_to_keep - current_balance
                
            if day_events or curr_date == req_date or curr_date == end_date:
                checkpoints.append(DailyBalanceCheckpoint(
                    date=curr_date,
                    balance_start=balance_start,
                    inflows=inflows,
                    outflows=outflows,
                    balance_end=current_balance,
                    events=day_events
                ))
                
            curr_date += timedelta(days=1)
            
        safe = first_violation is None
        
        safety = SafetyResult(
            safe=safe,
            minimum_balance=min_balance,
            minimum_balance_date=min_date,
            first_violation_date=first_violation,
            violation_amount=violation_amount
        )
        
        trace = SimulationTrace(
            request_id=request_context.request_id,
            start_date=req_date,
            end_date=end_date,
            opening_balance=state.current_balance,
            checkpoints=checkpoints,
            minimum_balance=min_balance,
            minimum_date=min_date,
            first_violation=first_violation,
            scenario_payments=overlay.candidate_payments if overlay else [],
            spending_overrides=overlay.spending_changes if overlay else []
        )
        
        return SimulationResult(trace=trace, safety=safety)

class EventCompressedSimulator:
    @staticmethod
    def simulate(
        state: CanonicalUserState,
        request_context: RequestContext,
        horizon_days: int = 90,
        overlay: ScenarioOverlay = None
    ) -> SimulationResult:
        
        req_date = request_context.request_date
        end_date = req_date + timedelta(days=horizon_days)
        
        events = build_event_calendar(state, req_date, horizon_days, overlay)
        events_by_date = defaultdict(list)
        for e in events:
            events_by_date[e.date].append(e)
            
        # Ensure we always process request_date and end_date
        if req_date not in events_by_date:
            events_by_date[req_date] = []
        if end_date not in events_by_date:
            events_by_date[end_date] = []
            
        sorted_dates = sorted(events_by_date.keys())
        
        current_balance = state.current_balance
        min_balance = current_balance
        min_date = req_date
        first_violation = None
        violation_amount = None
        
        checkpoints = []
        
        for curr_date in sorted_dates:
            balance_start = current_balance
            inflows = Decimal("0")
            outflows = Decimal("0")
            day_events = events_by_date[curr_date]
            
            for e in day_events:
                if e.direction == 'inflow':
                    inflows += e.amount
                    current_balance += e.amount
                else:
                    outflows += e.amount
                    current_balance -= e.amount
                    
            if current_balance < min_balance:
                min_balance = current_balance
                min_date = curr_date
                
            if current_balance < state.minimum_balance_to_keep and first_violation is None:
                first_violation = curr_date
                violation_amount = state.minimum_balance_to_keep - current_balance
                
            checkpoints.append(DailyBalanceCheckpoint(
                date=curr_date,
                balance_start=balance_start,
                inflows=inflows,
                outflows=outflows,
                balance_end=current_balance,
                events=day_events
            ))
            
        safe = first_violation is None
        
        safety = SafetyResult(
            safe=safe,
            minimum_balance=min_balance,
            minimum_balance_date=min_date,
            first_violation_date=first_violation,
            violation_amount=violation_amount
        )
        
        trace = SimulationTrace(
            request_id=request_context.request_id,
            start_date=req_date,
            end_date=end_date,
            opening_balance=state.current_balance,
            checkpoints=checkpoints,
            minimum_balance=min_balance,
            minimum_date=min_date,
            first_violation=first_violation,
            scenario_payments=overlay.candidate_payments if overlay else [],
            spending_overrides=overlay.spending_changes if overlay else []
        )
        
        return SimulationResult(trace=trace, safety=safety)

def simulate_baseline(state: CanonicalUserState, request_context: RequestContext, horizon_days: int = 90) -> SimulationResult:
    return EventCompressedSimulator.simulate(state, request_context, horizon_days)

def simulate_scenario(
    state: CanonicalUserState,
    request_context: RequestContext,
    candidate_payments: List[ForecastEvent],
    spending_changes: List[str],
    horizon_days: int = 90
) -> SimulationResult:
    overlay = ScenarioOverlay(
        candidate_payments=candidate_payments,
        spending_changes=spending_changes
    )
    return EventCompressedSimulator.simulate(state, request_context, horizon_days, overlay)
