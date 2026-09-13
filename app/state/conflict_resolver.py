from typing import List, Dict, Tuple, Optional
from datetime import date
from app.models.schemas import FinancialEvent
from app.models.state import CanonicalEvent, ResolutionTrace, EvidenceFact

def is_cancelled(status: str) -> bool:
    return status.lower() == 'cancelled'

def is_failed(status: str) -> bool:
    return status.lower() == 'failed'

def is_pending_credit(direction: str, status: str) -> bool:
    return direction.lower() == 'credit' and status.lower() == 'pending'

def is_settled(status: str) -> bool:
    return status.lower() == 'settled'

def is_unrealized_or_non_cash(status: str, direction: str) -> bool:
    return status.lower() == 'unrealized' or direction.lower() == 'non_cash'

def check_is_active_for_forecast(status: str, direction: str, category: str) -> bool:
    if is_cancelled(status) or is_failed(status):
        return False
    if is_pending_credit(direction, status):
        return False
    if is_unrealized_or_non_cash(status, direction):
        return False
    return True

def resolve_events(events: List[FinancialEvent], facts: List[EvidenceFact]) -> Tuple[List[CanonicalEvent], List[ResolutionTrace]]:
    traces = []
    
    events_sorted = sorted(events, key=lambda e: (e.event_date, e.event_id))
    
    canonical_map: Dict[str, CanonicalEvent] = {}
    for e in events_sorted:
        canonical_map[e.event_id] = CanonicalEvent(
            event_id=e.event_id,
            user_id=e.user_id,
            event_type=e.event_type,
            description=e.description,
            category=e.category,
            direction=e.direction,
            original_amount=e.amount,
            original_currency=e.currency,
            normalized_amount=None,
            home_currency="",
            conversion_rate=None,
            rate_date=None,
            event_date=e.event_date,
            settlement_date=e.settlement_date,
            status=e.status,
            linked_event_id=e.linked_event_id,
            flexibility=e.flexibility,
            minimum_allowed_amount=e.minimum_allowed_amount,
            resolution_source="financial_events.csv",
            is_unresolved_amount=(e.amount is None),
            is_active_for_forecast=check_is_active_for_forecast(e.status, e.direction, e.category)
        )
        
    for ce in list(canonical_map.values()):
        if ce.linked_event_id and ce.linked_event_id in canonical_map:
            prior_event = canonical_map[ce.linked_event_id]
            prior_event.superseded_by = ce.event_id
            prior_event.is_active_for_forecast = False
            ce.resolved_from = prior_event.event_id
            
            action = "superseded"
            if ce.status.lower() == 'cancelled':
                action = "cancelled"
            elif ce.status.lower() == 'settled' and prior_event.status.lower() != 'settled':
                action = "settled"
            else:
                action = "amended"
                
            traces.append(ResolutionTrace(
                event_id=prior_event.event_id,
                action=action,
                reason="lifecycle_link",
                source_record=ce.event_id,
                affected_record=prior_event.event_id
            ))

    for fact in sorted(facts, key=lambda f: f.fact_id):
        if fact.related_event_id and fact.related_event_id in canonical_map:
            target = canonical_map[fact.related_event_id]
            if fact.fact_type == 'cancellation':
                target.is_active_for_forecast = False
                target.status = 'cancelled'
                traces.append(ResolutionTrace(
                    event_id=target.event_id,
                    action="cancelled",
                    reason="evidence_fact",
                    source_record=fact.fact_id,
                    affected_record=target.event_id
                ))
            elif fact.fact_type == 'amount_update':
                old_amt = target.original_amount
                target.original_amount = fact.values.get('amount')
                target.original_currency = fact.values.get('currency', target.original_currency)
                target.is_unresolved_amount = (target.original_amount is None)
                target.resolution_source = fact.fact_id
                traces.append(ResolutionTrace(
                    event_id=target.event_id,
                    action="amended",
                    reason="evidence_fact",
                    source_record=fact.fact_id,
                    affected_record=target.event_id,
                    old_value=old_amt,
                    new_value=target.original_amount
                ))
            elif fact.fact_type == 'amendment':
                if 'status' in fact.values:
                    target.status = fact.values['status']
                    target.is_active_for_forecast = check_is_active_for_forecast(target.status, target.direction, target.category)
                traces.append(ResolutionTrace(
                    event_id=target.event_id,
                    action="amended",
                    reason="evidence_fact",
                    source_record=fact.fact_id,
                    affected_record=target.event_id
                ))
    
    seen = {}
    for ce in list(canonical_map.values()):
        if not ce.is_active_for_forecast:
            continue
        key = (ce.event_date, ce.original_amount, ce.original_currency, ce.description, ce.direction)
        if key in seen:
            prior_id = seen[key]
            ce.is_active_for_forecast = False
            ce.status = 'duplicate'
            traces.append(ResolutionTrace(
                event_id=ce.event_id,
                action="excluded",
                reason="duplicate",
                source_record=prior_id,
                affected_record=ce.event_id
            ))
        else:
            seen[key] = ce.event_id

    return list(canonical_map.values()), traces
