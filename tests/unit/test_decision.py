import unittest
from datetime import date, timedelta
from decimal import Decimal

from app.models.schemas import FinancialProfile, UserRequest, RequestPaymentOption
from app.models.state import CanonicalUserState, CanonicalEvent, RequestContext
from app.decision.models import PaymentInfo
from app.decision.evaluator import evaluate_request
from app.decision.generation import generate_candidate_plans

class TestDecision(unittest.TestCase):
    def setUp(self):
        self.req_date = date(2026, 1, 1)
        self.profile = FinancialProfile(
            user_id="user_1",
            home_currency="ZAR",
            current_available_balance=Decimal("30000"),
            minimum_balance_to_keep=Decimal("2000"),
            financial_priorities=[],
            expense_categories_to_protect=[],
            expense_categories_user_is_willing_to_reduce=[],
            expense_categories_user_is_willing_to_stop=[],
            payment_methods_user_will_consider=["full_payment", "partial_payment", "installments", "wait"],
            max_installment_months=None
        )
        
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

    def _make_state(self, events, profile=None):
        p = profile or self.profile
        return CanonicalUserState(
            user_id=p.user_id,
            home_currency=p.home_currency,
            current_balance=p.current_available_balance,
            minimum_balance_to_keep=p.minimum_balance_to_keep,
            balance_as_of_date=self.req_date,
            financial_priorities=p.financial_priorities,
            payment_methods_user_will_consider=p.payment_methods_user_will_consider,
            expense_categories_to_protect=p.expense_categories_to_protect,
            expense_categories_user_is_willing_to_reduce=p.expense_categories_user_is_willing_to_reduce,
            expense_categories_user_is_willing_to_stop=p.expense_categories_user_is_willing_to_stop,
            active_events=events,
        )
        
    def _make_context(self):
        return RequestContext(
            request_id=self.req.request_id,
            user_id=self.req.user_id,
            request_date=self.req.request_date,
            request_type=self.req.request_type,
            requested_amount=self.req.requested_amount,
            desired_completion_date=self.req.desired_completion_date,
            allows_partial_payment=self.req.allows_partial_payment,
            request_text=self.req.request_text,
            canonical_state=None
        )

    def test_affordable_now(self):
        state = self._make_state([])
        ctx = self._make_context()
        decision = evaluate_request(state, ctx, [])
        
        self.assertEqual(decision.affordability_status, "affordable_now")
        self.assertEqual(decision.amount_safe_to_pay, Decimal("5000"))
        self.assertEqual(decision.earliest_date_for_full_payment, self.req_date)
        self.assertEqual(decision.recommended_payment_method, "full_payment")

    def test_not_affordable(self):
        e1 = CanonicalEvent("E1", "user_1", "expense", "big", "big", "debit", Decimal("28000"), "ZAR", Decimal("28000"), "ZAR", Decimal("1"), self.req_date, self.req_date, None, "scheduled", None, "fixed", None, "csv", is_active_for_forecast=True)
        state = self._make_state([e1])
        ctx = self._make_context()
        decision = evaluate_request(state, ctx, [])
        
        self.assertEqual(decision.amount_safe_to_pay, Decimal("0"))
        self.assertEqual(decision.earliest_date_for_full_payment, None)
        self.assertEqual(decision.affordability_status, "not_affordable")

    def test_spending_changes(self):
        e1 = CanonicalEvent("E1", "user_1", "subscription", "gym", "gym", "debit", Decimal("6000"), "ZAR", Decimal("6000"), "ZAR", Decimal("1"), self.req_date, self.req_date, None, "scheduled", None, "stoppable", None, "csv", is_active_for_forecast=True, is_recurring=True, frequency="monthly", anchor_date=self.req_date)
        state = self._make_state([e1])
        ctx = self._make_context()
        decision = evaluate_request(state, ctx, [])
        
        self.assertEqual(decision.amount_safe_to_pay, Decimal("4000"))
        self.assertEqual(decision.affordability_status, "affordable_with_plan")
        self.assertEqual(decision.spending_changes_needed, ["stop:E1"])
        self.assertEqual(decision.recommended_payment_method, "full_payment")
        
    def test_wait_eligibility(self):
        # Earliest date is tomorrow
        state = self._make_state([])
        ctx = self._make_context()
        cands = generate_candidate_plans(state, ctx, Decimal("5000"), self.req_date + timedelta(days=1), [])
        methods = [c.payment_method for c in cands]
        self.assertIn("wait", methods)
        
        # Earliest date is today
        cands2 = generate_candidate_plans(state, ctx, Decimal("5000"), self.req_date, [])
        methods2 = [c.payment_method for c in cands2]
        self.assertNotIn("wait", methods2)

if __name__ == '__main__':
    unittest.main()
