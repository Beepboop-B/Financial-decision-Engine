from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import List, Dict, Optional, Tuple

@dataclass
class PaymentInfo:
    date: date
    amount: Decimal

@dataclass
class ValidationResult:
    safe: bool
    completed_by_deadline: bool
    minimum_projected_balance: Decimal
    minimum_balance_date: date
    errors: List[str] = field(default_factory=list)

@dataclass
class CandidatePlan:
    request_id: str
    payment_method: str
    payments: List[PaymentInfo]
    payment_option_id: Optional[str]
    spending_changes: List[str]
    
    # Derived statistics for ranking
    completion_date: Optional[date] = None
    total_paid: Decimal = Decimal('0')
    number_of_payments: int = 0
    first_payment_date: Optional[date] = None
    
    # Validation results
    validation: Optional[ValidationResult] = None
    ranking_key: Optional[Tuple] = None

@dataclass
class Decision:
    request_id: str
    amount_safe_to_pay: Decimal
    affordability_status: str
    recommended_payment_method: Optional[str]
    payment_plan: List[PaymentInfo]
    earliest_date_for_full_payment: Optional[date]
    spending_changes_needed: List[str]
    
    # Debug telemetry
    selected_candidate: Optional[CandidatePlan] = None
    debug_metrics: Dict[str, int] = field(default_factory=dict)
