import os
from app.ingestion.csv_loader import DataLoader
from app.state.builder import build_user_state, build_request_context
from app.decision.evaluator import evaluate_request
from app.decision.explanation import generate_explanation
from app.evidence.gemini_client import GeminiLLMClient
from app.evidence.llm_client import DummyLLMClient, ExtractionCache
from app.evidence.extractor import EvidenceExtractor
from app.evidence.models import ExtractionConfig
import json

class Orchestrator:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Orchestrator()
        return cls._instance
        
    def __init__(self):
        self.loader = DataLoader('dataset')
        self.loader.load_all()
        
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.mode = "live" if self.api_key else "offline"
        
        if self.mode == "live":
            self.client = GeminiLLMClient(api_key=self.api_key)
        else:
            self.client = DummyLLMClient({}) # Mock fallback
            
        self.cache = ExtractionCache()
        self.config = ExtractionConfig(max_batch_size=5)
        self.extractor = EvidenceExtractor(self.client, self.cache, self.config)
        
        self.msg_facts = self.extractor.extract_messages(self.loader.messages)
        self.img_facts = self.extractor.extract_images(self.loader.images)
        self.all_facts = self.msg_facts + self.img_facts
        
        self.eval_cache = {}

    def get_user(self, user_id: str):
        return next((p for p in self.loader.financial_profiles if p.user_id == user_id), None)
        
    def get_request(self, request_id: str):
        return next((r for r in self.loader.requests if r.request_id == request_id), None)
        
    def evaluate(self, request_id: str):
        if request_id in self.eval_cache:
            return self.eval_cache[request_id]
            
        req = self.get_request(request_id)
        if not req:
            return None
            
        profile = self.get_user(req.user_id)
        if not profile:
            return None
            
        user_events = [e for e in self.loader.financial_events if e.user_id == req.user_id]
        user_facts = [f for f in self.all_facts if f.user_id == req.user_id]
        
        state = build_user_state(
            profile=profile,
            events=user_events,
            facts=user_facts,
            exchange_rates=self.loader.exchange_rates,
            as_of_date=req.request_date
        )
        
        ctx = build_request_context(req, state)
        decision = evaluate_request(state, ctx, self.loader.request_payment_options)
        
        # We attach the explanation to decision so the API can use it
        decision.explanation = generate_explanation(decision)
        
        trace = None
        
        res = {
            "request_id": decision.request_id,
            "amount_safe_to_pay": float(decision.amount_safe_to_pay),
            "affordability_status": decision.affordability_status,
            "recommended_payment_method": decision.recommended_payment_method,
            "payment_plan": [
                {"date": str(p.date), "amount": float(p.amount)} for p in decision.payment_plan
            ] if decision.payment_plan else [],
            "earliest_date_for_full_payment": str(decision.earliest_date_for_full_payment) if decision.earliest_date_for_full_payment else None,
            "spending_changes_needed": decision.spending_changes_needed,
            "decision_explanation": decision.explanation,
            "trace": trace
        }
        
        self.eval_cache[request_id] = res
        return res
