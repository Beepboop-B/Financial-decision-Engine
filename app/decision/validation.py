from decimal import Decimal
from datetime import date, timedelta
from app.models.state import CanonicalUserState, RequestContext
from app.simulation.models import ForecastEvent
from app.simulation.simulator import simulate_scenario
from app.decision.models import CandidatePlan, ValidationResult, PaymentInfo

def validate_candidate(
    plan: CandidatePlan,
    state: CanonicalUserState,
    ctx: RequestContext,
    metrics: dict
) -> ValidationResult:
    errors = []
    
    if plan.payment_method != 'wait' and plan.payment_method not in state.payment_methods_user_will_consider:
        errors.append("Payment method not accepted by user")
        
    total_paid = Decimal('0')
    last_date = None
    end_date = ctx.request_date + timedelta(days=90)
    for p in plan.payments:
        if p.amount < 0:
            errors.append("Negative payment amount")
        if p.date < ctx.request_date or p.date > end_date:
            errors.append("Payment date out of forecast horizon")
        if last_date and p.date < last_date:
            errors.append("Payments not chronological")
        last_date = p.date
        total_paid += p.amount
        
    if plan.payment_method != 'installments' and total_paid != ctx.requested_amount:
        errors.append(f"Total paid {total_paid} != requested {ctx.requested_amount}")
        
    if last_date and last_date > ctx.desired_completion_date:
        errors.append(f"Completes on {last_date} which is past deadline {ctx.desired_completion_date}")
        
    if len(plan.spending_changes) > 3:
        errors.append(">3 spending changes")
    
    active_dict = {ce.event_id: ce for ce in state.active_events}
    stops = set()
    reductions = set()
    for sc in plan.spending_changes:
        parts = sc.split(':')
        eid = parts[1]
        if eid not in active_dict:
            errors.append(f"Event {eid} not active")
        else:
            if active_dict[eid].flexibility not in ('stoppable', 'reducible', 'reducible_or_stoppable'):
                errors.append(f"Cannot change non-flexible event {eid}")
        
        if parts[0] == 'stop':
            stops.add(eid)
        elif parts[0] == 'reduce_to':
            reductions.add(eid)
            
    if stops.intersection(reductions):
        errors.append("Event both stopped and reduced")
        
    if errors:
        return ValidationResult(safe=False, completed_by_deadline=False, minimum_projected_balance=Decimal('0'), minimum_balance_date=ctx.request_date, errors=errors)
        
    forecast_events = []
    for i, p in enumerate(plan.payments):
        forecast_events.append(ForecastEvent(
            date=p.date,
            event_id=f"candidate_pay_{i}",
            amount=p.amount,
            direction="outflow",
            category="request",
            source_type="candidate",
            event_type="test",
            priority=1
        ))
        
    metrics['simulations'] = metrics.get('simulations', 0) + 1
    res = simulate_scenario(state, ctx, candidate_payments=forecast_events, spending_changes=plan.spending_changes)
    
    if not res.safety.safe:
        errors.append("Unsafe: minimum balance violated")
        
    plan.completion_date = last_date
    plan.total_paid = total_paid
    plan.number_of_payments = len(plan.payments)
    plan.first_payment_date = plan.payments[0].date if plan.payments else None
    
    return ValidationResult(
        safe=res.safety.safe,
        completed_by_deadline=(last_date <= ctx.desired_completion_date if last_date else True),
        minimum_projected_balance=res.safety.minimum_balance,
        minimum_balance_date=res.safety.minimum_balance_date,
        errors=errors
    )
