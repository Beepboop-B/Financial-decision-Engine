from datetime import date, timedelta
from decimal import Decimal
from typing import Optional, Tuple
from app.models.state import CanonicalUserState, RequestContext
from app.simulation.models import ForecastEvent, ScenarioOverlay
from app.simulation.simulator import simulate_scenario

def calculate_amount_safe_to_pay(
    state: CanonicalUserState,
    ctx: RequestContext,
    metrics: dict
) -> Decimal:
    """
    Binary search for the max safe amount to pay on request_date, [0, requested_amount].
    Does NOT use optional spending changes.
    """
    low_cents = 0
    high_cents = int(ctx.requested_amount * 100)
    best_safe_cents = 0
    
    while low_cents <= high_cents:
        mid_cents = (low_cents + high_cents) // 2
        mid_amount = Decimal(mid_cents) / Decimal("100")
        
        payment = ForecastEvent(
            date=ctx.request_date,
            event_id="cap_test",
            amount=mid_amount,
            direction="outflow",
            category="request",
            source_type="request",
            event_type="test",
            priority=1
        )
        
        metrics['simulations'] = metrics.get('simulations', 0) + 1
        res = simulate_scenario(state, ctx, candidate_payments=[payment], spending_changes=[])
        
        if res.safety.safe:
            best_safe_cents = mid_cents
            low_cents = mid_cents + 1
        else:
            high_cents = mid_cents - 1
            
    return Decimal(best_safe_cents) / Decimal("100")

def calculate_earliest_date_for_full_payment(
    state: CanonicalUserState,
    ctx: RequestContext,
    metrics: dict
) -> Optional[date]:
    """
    Finds the earliest date within the 90-day forecast where paying the FULL requested amount is safe.
    Chronological search starting from request_date.
    Does NOT use optional spending changes.
    """
    end_date = ctx.request_date + timedelta(days=90)
    curr_date = ctx.request_date
    
    # We can do event-boundary search, but chronological is foolproof and max 90 steps.
    while curr_date <= end_date:
        payment = ForecastEvent(
            date=curr_date,
            event_id="earliest_test",
            amount=ctx.requested_amount,
            direction="outflow",
            category="request",
            source_type="request",
            event_type="test",
            priority=1
        )
        
        metrics['simulations'] = metrics.get('simulations', 0) + 1
        res = simulate_scenario(state, ctx, candidate_payments=[payment], spending_changes=[])
        
        if res.safety.safe:
            return curr_date
            
        curr_date += timedelta(days=1)
        
    return None
