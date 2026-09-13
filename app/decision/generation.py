import itertools
from decimal import Decimal
from typing import List, Optional
from datetime import timedelta, date
from app.models.state import CanonicalUserState, RequestContext
from app.models.schemas import RequestPaymentOption
from app.decision.models import CandidatePlan, PaymentInfo

def generate_spending_change_combinations(state: CanonicalUserState) -> List[List[str]]:
    candidates = []
    for ce in state.active_events:
        if ce.is_recurring and ce.flexibility in ('stoppable', 'reducible', 'reducible_or_stoppable'):
            if ce.category in state.expense_categories_to_protect:
                continue
                
            eid = ce.event_id
            if ce.flexibility in ('stoppable', 'reducible_or_stoppable'):
                candidates.append(f"stop:{eid}")
            if ce.flexibility in ('reducible', 'reducible_or_stoppable'):
                if ce.minimum_allowed_amount is not None:
                    candidates.append(f"reduce_to:{eid}:{ce.minimum_allowed_amount}")
                    
    combinations = [[]]
    
    for c in candidates:
        combinations.append([c])
        
    for combo in itertools.combinations(candidates, 2):
        events_involved = set(c.split(':')[1] for c in combo)
        if len(events_involved) == 2:
            combinations.append(list(combo))
            
    for combo in itertools.combinations(candidates, 3):
        events_involved = set(c.split(':')[1] for c in combo)
        if len(events_involved) == 3:
            combinations.append(list(combo))
            
    return combinations

def generate_candidate_plans(
    state: CanonicalUserState,
    ctx: RequestContext,
    safe_amount: Decimal,
    earliest_date: Optional[date],
    payment_options: List[RequestPaymentOption]
) -> List[CandidatePlan]:
    
    plans = []
    sc_combos = generate_spending_change_combinations(state)
    
    for sc in sc_combos:
        if 'full_payment' in state.payment_methods_user_will_consider:
            plans.append(CandidatePlan(
                request_id=ctx.request_id,
                payment_method='full_payment',
                payments=[PaymentInfo(date=ctx.request_date, amount=ctx.requested_amount)],
                payment_option_id=None,
                spending_changes=sc
            ))
            
        if ctx.allows_partial_payment and 'partial_payment' in state.payment_methods_user_will_consider:
            if 0 < safe_amount < ctx.requested_amount and earliest_date and earliest_date <= ctx.desired_completion_date:
                plans.append(CandidatePlan(
                    request_id=ctx.request_id,
                    payment_method='partial_payment',
                    payments=[
                        PaymentInfo(date=ctx.request_date, amount=safe_amount),
                        PaymentInfo(date=earliest_date, amount=ctx.requested_amount - safe_amount)
                    ],
                    payment_option_id=None,
                    spending_changes=sc
                ))
                
        # Wait is eligible when full payment becomes safe LATER, and user accepts full_payment
        if 'full_payment' in state.payment_methods_user_will_consider and earliest_date and earliest_date > ctx.request_date and earliest_date <= ctx.desired_completion_date:
            plans.append(CandidatePlan(
                request_id=ctx.request_id,
                payment_method='wait',
                payments=[PaymentInfo(date=earliest_date, amount=ctx.requested_amount)],
                payment_option_id=None,
                spending_changes=sc
            ))
            
        if 'installments' in state.payment_methods_user_will_consider:
            for opt in payment_options:
                if opt.request_id == ctx.request_id:
                    pmts = []
                    curr = opt.first_payment_date
                    for _ in range(opt.number_of_payments):
                        pmts.append(PaymentInfo(date=curr, amount=opt.payment_amount))
                        days = opt.payment_frequency_days if opt.payment_frequency_days is not None else 30
                        curr += timedelta(days=days)
                        
                    plans.append(CandidatePlan(
                        request_id=ctx.request_id,
                        payment_method='installments',
                        payments=pmts,
                        payment_option_id=opt.payment_option_id,
                        spending_changes=sc
                    ))
                    
    return plans
