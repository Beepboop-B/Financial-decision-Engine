from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import List, Dict, Optional, Any

@dataclass(frozen=True)
class ForecastEvent:
    date: date
    event_id: str
    amount: Decimal
    direction: str  # 'inflow' or 'outflow'
    category: str
    source_type: str
    event_type: str
    priority: int
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ScenarioOverlay:
    # Example candidate payments
    candidate_payments: List[ForecastEvent] = field(default_factory=list)
    # List of changes like "stop:event_id" or "reduce_to:event_id:new_amount"
    spending_changes: List[str] = field(default_factory=list)

@dataclass
class DailyBalanceCheckpoint:
    date: date
    balance_start: Decimal
    inflows: Decimal
    outflows: Decimal
    balance_end: Decimal
    events: List[ForecastEvent]

@dataclass
class SimulationTrace:
    request_id: str
    start_date: date
    end_date: date
    opening_balance: Decimal
    checkpoints: List[DailyBalanceCheckpoint]
    minimum_balance: Decimal
    minimum_date: date
    first_violation: Optional[date]
    scenario_payments: List[ForecastEvent]
    spending_overrides: List[str]

@dataclass
class SafetyResult:
    safe: bool
    minimum_balance: Decimal
    minimum_balance_date: date
    first_violation_date: Optional[date]
    violation_amount: Optional[Decimal]

@dataclass
class SimulationResult:
    trace: SimulationTrace
    safety: SafetyResult
