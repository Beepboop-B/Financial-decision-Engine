import unittest
from fastapi.testclient import TestClient
from app.api.app import app

class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("mode", data)

    def test_list_users(self):
        response = self.client.get("/users")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(len(data) > 0)

    def test_get_user(self):
        response = self.client.get("/users/user_01")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["user_id"], "user_01")

    def test_unknown_user(self):
        response = self.client.get("/users/unknown_123")
        self.assertEqual(response.status_code, 404)

    def test_evaluate_request(self):
        response = self.client.post("/requests/request_26/evaluate")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["request_id"], "request_26")
        self.assertIn("amount_safe_to_pay", data)
        self.assertIn("decision_explanation", data)

    def test_create_request(self):
        payload = {
            "user_id": "user_01",
            "request_text": "MacBook Pro",
            "requested_amount": 60000.0,
            "currency": "INR",
            "desired_completion_date": "2026-10-01",
            "request_type": "purchase",
            "allows_partial_payment": True,
            "payment_methods": ["full_payment", "partial_payment"]
        }
        res = self.client.post("/requests", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("request_id", data)
        
        req_id = data["request_id"]
        eval_res = self.client.post(f"/requests/{req_id}/evaluate")
        self.assertEqual(eval_res.status_code, 200)

    def test_api_engine_separation(self):
        # We test that the API output matches direct service evaluation logically
        from app.services.evaluation_service import Orchestrator
        orchestrator = Orchestrator.get_instance()
        direct = orchestrator.evaluate("request_26")
        
        response = self.client.post("/requests/request_26/evaluate")
        api_decision = response.json()
        
        self.assertEqual(direct["amount_safe_to_pay"], api_decision["amount_safe_to_pay"])
        self.assertEqual(direct["affordability_status"], api_decision["affordability_status"])

    def test_batch_evaluate(self):
        # request_27 is probably another one, let's just use request_26 twice or find another
        response = self.client.post("/evaluate/batch", json={"request_ids": ["request_26", "request_26"]})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["completed"], 2)
        
    def test_evidence(self):
        response = self.client.get("/requests/request_26/evidence")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.json(), list))

    def test_trace(self):
        response = self.client.get("/requests/request_26/trace")
        self.assertEqual(response.status_code, 200)

    def test_usage(self):
        response = self.client.get("/usage")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_llm_calls", data)

if __name__ == '__main__':
    unittest.main()
