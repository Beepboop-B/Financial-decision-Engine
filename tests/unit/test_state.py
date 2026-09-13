import unittest
from datetime import date
from decimal import Decimal
import copy

from app.models.schemas import FinancialProfile, FinancialEvent, UserRequest, ExchangeRate
from app.models.state import EvidenceFact, ScenarioState, CanonicalUserState
from app.state.builder import build_user_state, build_request_context
from app.state.conflict_resolver import check_is_active_for_forecast

class TestStateEngine(unittest.TestCase):
    def setUp(self):
        self.profile = FinancialProfile(
            user_id="user_1",
            home_currency="ZAR",
            current_available_balance=Decimal("10000"),
            minimum_balance_to_keep=Decimal("2000"),
            financial_priorities=["education"],
            expense_categories_to_protect=["rent"],
            expense_categories_user_is_willing_to_reduce=[],
            expense_categories_user_is_willing_to_stop=[],
            payment_methods_user_will_consider=["full_payment"],
            max_installment_months=None
        )
        self.rates = [
            ExchangeRate(date(2026, 1, 1), "USD", "ZAR", Decimal("18.0"))
        ]
        
    def test_conflict_resolution_lifecycle(self):
        events = [
            FinancialEvent("E1", "user_1", "expense", "desc", "other", "debit", Decimal("100"), "ZAR", date(2026,1,1), None, "estimated", None, "fixed", None),
            FinancialEvent("E2", "user_1", "expense", "desc", "other", "debit", Decimal("150"), "ZAR", date(2026,1,1), None, "settled", "E1", "fixed", None)
        ]
        state = build_user_state(self.profile, events, [], self.rates, date(2026,1,2))
        
        # E1 should be superseded, E2 active (or historical if before as_of_date)
        # Since as_of_date is 2026-01-02 and events are on 2026-01-01 and not recurring, they will be historical if active
        e1_canonical = next(e for e in state.excluded_events if e.event_id == "E1")
        e2_canonical = next(e for e in state.historical_events if e.event_id == "E2")
        
        self.assertFalse(e1_canonical.is_active_for_forecast)
        self.assertEqual(e1_canonical.superseded_by, "E2")
        self.assertTrue(e2_canonical.is_active_for_forecast)
        
    def test_evidence_fact_cancellation(self):
        events = [
            FinancialEvent("E1", "user_1", "recurring", "gym", "gym", "debit", Decimal("100"), "ZAR", date(2026,1,1), None, "estimated", None, "fixed", None)
        ]
        facts = [
            EvidenceFact("F1", "message", "M1", "user_1", "E1", "cancellation", {}, date(2026,1,1), 1.0, "llm")
        ]
        state = build_user_state(self.profile, events, facts, self.rates, date(2026,1,1))
        
        # E1 should be cancelled
        e1_canonical = next(e for e in state.excluded_events if e.event_id == "E1")
        self.assertEqual(e1_canonical.status, "cancelled")
        self.assertFalse(e1_canonical.is_active_for_forecast)
        
    def test_immutability(self):
        events = [
            FinancialEvent("E1", "user_1", "recurring", "gym", "gym", "debit", Decimal("100"), "ZAR", date(2026,1,1), None, "estimated", None, "fixed", None)
        ]
        state_A = build_user_state(self.profile, events, [], self.rates, date(2026,1,1))
        
        # Simulate creating a scenario and modifying the candidate lists
        scenario_A = ScenarioState(baseline=state_A)
        scenario_A.candidate_spending_changes.append("stop:E1")
        
        scenario_B = ScenarioState(baseline=state_A)
        scenario_B.candidate_spending_changes.append("reduce_to:E1:50")
        
        self.assertEqual(len(state_A.active_events), 1)
        # Check that state_A is unchanged
        self.assertEqual(len(scenario_A.baseline.active_events), 1)
        self.assertEqual(len(scenario_B.candidate_spending_changes), 1)
        self.assertNotEqual(scenario_A.candidate_spending_changes, scenario_B.candidate_spending_changes)

    def test_unresolved_amount(self):
        events = [
            FinancialEvent("E1", "user_1", "recurring", "gym", "gym", "debit", None, "ZAR", date(2026,1,1), None, "estimated", None, "fixed", None)
        ]
        state = build_user_state(self.profile, events, [], self.rates, date(2026,1,1))
        self.assertEqual(len(state.unresolved_events), 1)
        self.assertTrue(state.unresolved_events[0].is_unresolved_amount)

    def test_currency_normalization(self):
        events = [
            FinancialEvent("E1", "user_1", "recurring", "gym", "gym", "debit", Decimal("100"), "USD", date(2026,1,1), None, "estimated", None, "fixed", None)
        ]
        state = build_user_state(self.profile, events, [], self.rates, date(2026,1,1))
        e1 = state.active_events[0]
        self.assertEqual(e1.normalized_amount, Decimal("1800"))
        
if __name__ == '__main__':
    unittest.main()
