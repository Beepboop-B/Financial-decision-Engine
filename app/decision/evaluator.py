from typing import List, Optional
from decimal import Decimal
from datetime import date
from app.models.schemas import RequestPaymentOption
from app.models.state import CanonicalUserState, RequestContext
from app.decision.models import Decision, CandidatePlan
from app.decision.capacity import calculate_amount_safe_to_pay, calculate_earliest_date_for_full_payment
from app.decision.generation import generate_candidate_plans
from app.decision.validation import validate_candidate
from app.decision.ranking import build_ranking_key

def evaluate_request(
    state: CanonicalUserState,
    ctx: RequestContext,
    payment_options: List[RequestPaymentOption]
) -> Decision:
    metrics = {'simulations': 0, 'candidates_generated': 0, 'candidates_safe': 0}
    
    # 1. Capacity
    amount_safe = calculate_amount_safe_to_pay(state, ctx, metrics)
    earliest_date = calculate_earliest_date_for_full_payment(state, ctx, metrics)
    
    # 2. Generation
    # We only pass baseline safe amounts into generation so we don't accidentally
    # claim a partial payment is safe when it relies on a spending change.
    candidates = generate_candidate_plans(state, ctx, amount_safe, earliest_date, payment_options)
    metrics['candidates_generated'] = len(candidates)
    
    # 3. Validation & Ranking
    valid_candidates = []
    for c in candidates:
        val = validate_candidate(c, state, ctx, metrics)
        c.validation = val
        if val.safe and not val.errors:
            c.ranking_key = build_ranking_key(c)
            valid_candidates.append(c)
            metrics['candidates_safe'] += 1
            
    # 4. Selection
    selected = None
    if valid_candidates:
        # Sort ascending since we designed ranking key to minimize
        valid_candidates.sort(key=lambda x: x.ranking_key)
        selected = valid_candidates[0]
        
    # 5. Status Classification
    status = "not_affordable"
    if selected:
        if amount_safe == ctx.requested_amount and selected.payment_method == 'full_payment' and not selected.spending_changes:
            status = "affordable_now"
        elif selected.payment_method == 'wait' and not selected.spending_changes:
            status = "affordable_later"
        else:
            status = "affordable_with_plan"
            
    # 6. Build Decision
    decision = Decision(
        request_id=ctx.request_id,
        amount_safe_to_pay=amount_safe,
        affordability_status=status,
        recommended_payment_method=selected.payment_method if selected else None,
        payment_plan=selected.payments if selected else [],
        earliest_date_for_full_payment=earliest_date,
        spending_changes_needed=selected.spending_changes if selected else [],
        selected_candidate=selected,
        debug_metrics=metrics
    )
    
    return decision
