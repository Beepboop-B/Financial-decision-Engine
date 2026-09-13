from dataclasses import dataclass, field
from typing import List, Optional, Dict, Set, Any
from datetime import date
from decimal import Decimal

@dataclass
class EvidenceFact:
    fact_id: str
    source_type: str
    source_id: str
    user_id: str
    related_event_id: Optional[str]
    fact_type: str 
    values: Dict[str, Any]
    effective_date: Optional[date]
    confidence: float
    extraction_method: str

@dataclass
class CanonicalEvent:
    event_id: str
    user_id: str
    event_type: str
    description: str
    category: str
    direction: str
    original_amount: Optional[Decimal]
    original_currency: str
    normalized_amount: Optional[Decimal]
    home_currency: str
    conversion_rate: Optional[Decimal]
    rate_date: Optional[date]
    event_date: date
    settlement_date: Optional[date]
    status: str
    linked_event_id: Optional[str]
    flexibility: str
    minimum_allowed_amount: Optional[Decimal]
    resolution_source: str
    resolved_from: Optional[str] = None
    superseded_by: Optional[str] = None
    is_active_for_forecast: bool = False
    is_unresolved_amount: bool = False
    
    # Recurrence fields
    is_recurring: bool = False
    frequency: Optional[str] = None  # 'monthly', 'weekly', 'biweekly'
    anchor_date: Optional[date] = None

@dataclass
class ResolutionTrace:
    event_id: str
    action: str
    reason: str
    source_record: str
    affected_record: Optional[str] = None
    old_value: Any = None
    new_value: Any = None

@dataclass
class CanonicalUserState:
    user_id: str
    home_currency: str
    current_balance: Decimal
    minimum_balance_to_keep: Decimal
    balance_as_of_date: date
    financial_priorities: List[str]
    payment_methods_user_will_consider: List[str]
    expense_categories_to_protect: List[str]
    expense_categories_user_is_willing_to_reduce: List[str]
    expense_categories_user_is_willing_to_stop: List[str]
    
    active_events: List[CanonicalEvent] = field(default_factory=list)
    historical_events: List[CanonicalEvent] = field(default_factory=list)
    excluded_events: List[CanonicalEvent] = field(default_factory=list)
    unresolved_events: List[CanonicalEvent] = field(default_factory=list)
    
    resolution_traces: List[ResolutionTrace] = field(default_factory=list)
    applied_evidence_facts: List[EvidenceFact] = field(default_factory=list)

@dataclass
class RequestContext:
    request_id: str
    user_id: str
    request_date: date
    request_type: str
    requested_amount: Decimal
    desired_completion_date: date
    allows_partial_payment: bool
    request_text: str
    canonical_state: CanonicalUserState

@dataclass
class ScenarioState:
    baseline: CanonicalUserState
    candidate_spending_changes: List[str] = field(default_factory=list)
    candidate_payments: List[Dict[str, Any]] = field(default_factory=list)
