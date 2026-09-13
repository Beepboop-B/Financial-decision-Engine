import unittest
from datetime import date, timedelta
from decimal import Decimal

from app.models.schemas import FinancialProfile, FinancialEvent, UserRequest, ExchangeRate
from app.models.state import CanonicalUserState, CanonicalEvent, RequestContext
from app.simulation.models import ForecastEvent, ScenarioOverlay
from app.simulation.simulator import ReferenceSimulator, EventCompressedSimulator

class TestSimulation(unittest.TestCase):
    def setUp(self):
        self.profile = FinancialProfile(
            user_id="user_1",
            home_currency="ZAR",
            current_available_balance=Decimal("10000"),
            minimum_balance_to_keep=Decimal("2000"),
            financial_priorities=["education"],
            expense_categories_to_protect=["rent"],
            expense_categories_user_is_willing_to_reduce=[],
            expense_categories_user_is_willing_to_stop=["gym"],
            payment_methods_user_will_consider=["full_payment"],
            max_installment_months=None
        )
        self.req_date = date(2026, 1, 1)
        
        self.req = UserRequest(
            request_id="R1",
            user_id="user_1",
            request_date=self.req_date,
            request_type="purchase",
            requested_amount=Decimal("5000"),
            desired_completion_date=self.req_date + timedelta(days=10),
            allows_partial_payment=True,
            request_text="dummy"
        )
        
    def _make_state(self, events):
        return CanonicalUserState(
            user_id=self.profile.user_id,
            home_currency=self.profile.home_currency,
            current_balance=self.profile.current_available_balance,
            minimum_balance_to_keep=self.profile.minimum_balance_to_keep,
            balance_as_of_date=self.req_date,
            financial_priorities=self.profile.financial_priorities,
            payment_methods_user_will_consider=self.profile.payment_methods_user_will_consider,
            expense_categories_to_protect=self.profile.expense_categories_to_protect,
            expense_categories_user_is_willing_to_reduce=self.profile.expense_categories_user_is_willing_to_reduce,
            expense_categories_user_is_willing_to_stop=self.profile.expense_categories_user_is_willing_to_stop,
            active_events=events,
        )
        
    def _make_context(self, state):
        return RequestContext(
            request_id=self.req.request_id,
            user_id=self.req.user_id,
            request_date=self.req.request_date,
            request_type=self.req.request_type,
            requested_amount=self.req.requested_amount,
            desired_completion_date=self.req.desired_completion_date,
            allows_partial_payment=self.req.allows_partial_payment,
            request_text=self.req.request_text,
            canonical_state=state
        )
        
    def assert_simulators_match(self, state, ctx, overlay=None):
        ref_res = ReferenceSimulator.simulate(state, ctx, overlay=overlay)
        opt_res = EventCompressedSimulator.simulate(state, ctx, overlay=overlay)
        
        self.assertEqual(ref_res.safety.safe, opt_res.safety.safe)
        self.assertEqual(ref_res.safety.minimum_balance, opt_res.safety.minimum_balance)
        self.assertEqual(ref_res.safety.minimum_balance_date, opt_res.safety.minimum_balance_date)
        self.assertEqual(ref_res.safety.first_violation_date, opt_res.safety.first_violation_date)
        
        ref_final = ref_res.trace.checkpoints[-1]
        opt_final = opt_res.trace.checkpoints[-1]
        self.assertEqual(ref_final.balance_end, opt_final.balance_end)

    def test_no_future_events(self):
        state = self._make_state([])
        ctx = self._make_context(state)
        self.assert_simulators_match(state, ctx)
        opt_res = EventCompressedSimulator.simulate(state, ctx)
        self.assertTrue(opt_res.safety.safe)
        self.assertEqual(opt_res.safety.minimum_balance, Decimal("10000"))

    def test_recurring_expense(self):
        e1 = CanonicalEvent("E1", "user_1", "subscription", "gym", "gym", "debit", Decimal("100"), "ZAR", Decimal("100"), "ZAR", Decimal("1"), self.req_date, date(2025,12,1), None, "settled", None, "stoppable", None, "csv", is_recurring=True, frequency="monthly", anchor_date=date(2025,12,1), is_active_for_forecast=True)
        state = self._make_state([e1])
        ctx = self._make_context(state)
        self.assert_simulators_match(state, ctx)
        opt_res = EventCompressedSimulator.simulate(state, ctx)
        self.assertTrue(opt_res.safety.safe)
        # Jan 1, Feb 1, Mar 1, Apr 1 (Apr 1 is exactly 90 days from Jan 1 in non-leap year 2026) -> 4 times -> 400
        self.assertEqual(opt_res.trace.checkpoints[-1].balance_end, Decimal("9600"))

    def test_spending_change_overlay(self):
        e1 = CanonicalEvent("E1", "user_1", "subscription", "gym", "gym", "debit", Decimal("100"), "ZAR", Decimal("100"), "ZAR", Decimal("1"), self.req_date, date(2025,12,1), None, "settled", None, "stoppable", None, "csv", is_recurring=True, frequency="monthly", anchor_date=date(2025,12,1), is_active_for_forecast=True)
        state = self._make_state([e1])
        ctx = self._make_context(state)
        overlay = ScenarioOverlay(spending_changes=["stop:E1"])
        
        self.assert_simulators_match(state, ctx, overlay)
        opt_res = EventCompressedSimulator.simulate(state, ctx, overlay=overlay)
        
        self.assertEqual(opt_res.trace.checkpoints[-1].balance_end, Decimal("10000"))

    def test_safety_violation(self):
        e1 = CanonicalEvent("E1", "user_1", "expense", "big", "big", "debit", Decimal("9000"), "ZAR", Decimal("9000"), "ZAR", Decimal("1"), self.req_date, date(2026,1,5), None, "scheduled", None, "fixed", None, "csv", is_active_for_forecast=True)
        state = self._make_state([e1])
        ctx = self._make_context(state)
        self.assert_simulators_match(state, ctx)
        
        opt_res = EventCompressedSimulator.simulate(state, ctx)
        self.assertFalse(opt_res.safety.safe)
        self.assertEqual(opt_res.safety.first_violation_date, date(2026,1,5))
        self.assertEqual(opt_res.safety.minimum_balance, Decimal("1000"))

if __name__ == '__main__':
    unittest.main()
