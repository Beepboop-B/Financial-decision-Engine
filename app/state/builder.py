from typing import List, Dict, Tuple, Optional
from datetime import date, timedelta
from decimal import Decimal
from app.models.schemas import FinancialProfile, FinancialEvent, UserRequest, ExchangeRate
from app.models.state import CanonicalUserState, CanonicalEvent, RequestContext, EvidenceFact
from app.state.conflict_resolver import resolve_events

def detect_recurrence(events: List[CanonicalEvent]) -> None:
    groups: Dict[Tuple[str, str, str], List[CanonicalEvent]] = {}
    for ce in events:
        if ce.is_unresolved_amount or ce.status in ('cancelled', 'failed', 'duplicate') or ce.superseded_by:
            continue
        key = (ce.description, ce.direction, ce.category)
        if key not in groups:
            groups[key] = []
        groups[key].append(ce)
        
    for key, group in groups.items():
        if len(group) < 2:
            ce = group[0]
            desc_lower = ce.description.lower()
            cat_lower = ce.category.lower()
            if ce.event_type == 'subscription' or 'salary' in desc_lower or cat_lower == 'salary' or 'rent' in desc_lower or cat_lower == 'rent':
                ce.is_recurring = True
                ce.frequency = 'monthly'
                ce.anchor_date = ce.event_date
                ce.is_active_for_forecast = True
            continue
            
        group.sort(key=lambda x: x.event_date)
        intervals = [(group[i].event_date - group[i-1].event_date).days for i in range(1, len(group))]
        
        avg_interval = sum(intervals) / len(intervals)
        
        freq = None
        if 25 <= avg_interval <= 35:
            freq = 'monthly'
        elif 6 <= avg_interval <= 8:
            freq = 'weekly'
        elif 13 <= avg_interval <= 15:
            freq = 'biweekly'
            
        if freq:
            latest = group[-1]
            latest.is_recurring = True
            latest.frequency = freq
            latest.anchor_date = latest.event_date
            latest.is_active_for_forecast = True

def build_user_state(
    profile: FinancialProfile,
    events: List[FinancialEvent],
    facts: List[EvidenceFact],
    exchange_rates: List[ExchangeRate],
    as_of_date: date
) -> CanonicalUserState:
    
    canonical_events, traces = resolve_events(events, facts)
    
    rate_map = {(r.rate_date, r.from_currency, r.to_currency): r.rate for r in exchange_rates}
    
    for ce in canonical_events:
        ce.home_currency = profile.home_currency
        if ce.original_currency == profile.home_currency:
            ce.normalized_amount = ce.original_amount
            ce.conversion_rate = Decimal('1.0')
            ce.rate_date = ce.event_date
        elif ce.original_amount is not None:
            rate = rate_map.get((ce.event_date, ce.original_currency, profile.home_currency))
            if rate is not None:
                ce.normalized_amount = ce.original_amount * rate
                ce.conversion_rate = rate
                ce.rate_date = ce.event_date
            else:
                prior_rates = [r for r in exchange_rates if r.from_currency == ce.original_currency 
                               and r.to_currency == profile.home_currency and r.rate_date <= ce.event_date]
                if prior_rates:
                    best_rate = max(prior_rates, key=lambda x: x.rate_date)
                    ce.normalized_amount = ce.original_amount * best_rate.rate
                    ce.conversion_rate = best_rate.rate
                    ce.rate_date = best_rate.rate_date
                else:
                    ce.is_unresolved_amount = True
                    ce.normalized_amount = None
                    
    detect_recurrence(canonical_events)
        
    active = []
    historical = []
    excluded = []
    unresolved = []
    
    for ce in canonical_events:
        if ce.is_unresolved_amount:
            unresolved.append(ce)
        elif not ce.is_active_for_forecast:
            if ce.status in ('cancelled', 'failed', 'duplicate') or ce.superseded_by:
                excluded.append(ce)
            else:
                historical.append(ce)
        else:
            if ce.event_date < as_of_date and not ce.is_recurring:
                historical.append(ce)
            else:
                active.append(ce)
                
    state = CanonicalUserState(
        user_id=profile.user_id,
        home_currency=profile.home_currency,
        current_balance=profile.current_available_balance,
        minimum_balance_to_keep=profile.minimum_balance_to_keep,
        balance_as_of_date=as_of_date,
        financial_priorities=profile.financial_priorities,
        payment_methods_user_will_consider=profile.payment_methods_user_will_consider,
        expense_categories_to_protect=profile.expense_categories_to_protect,
        expense_categories_user_is_willing_to_reduce=profile.expense_categories_user_is_willing_to_reduce,
        expense_categories_user_is_willing_to_stop=profile.expense_categories_user_is_willing_to_stop,
        active_events=active,
        historical_events=historical,
        excluded_events=excluded,
        unresolved_events=unresolved,
        resolution_traces=traces,
        applied_evidence_facts=facts
    )
    return state

def build_request_context(
    request: UserRequest,
    canonical_state: CanonicalUserState
) -> RequestContext:
    return RequestContext(
        request_id=request.request_id,
        user_id=request.user_id,
        request_date=request.request_date,
        request_type=request.request_type,
        requested_amount=request.requested_amount,
        desired_completion_date=request.desired_completion_date,
        allows_partial_payment=request.allows_partial_payment,
        request_text=request.request_text,
        canonical_state=canonical_state
    )
