from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any
from app.services.evaluation_service import Orchestrator

app = FastAPI(title="Buy or Wait Financial Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class HealthResponse(BaseModel):
    status: str
    version: str
    mode: str

@app.get("/health", response_model=HealthResponse)
def get_health():
    orchestrator = Orchestrator.get_instance()
    return HealthResponse(
        status="ok",
        version="1.0.0",
        mode=orchestrator.mode
    )

@app.get("/users")
def list_users():
    orchestrator = Orchestrator.get_instance()
    return [{"user_id": p.user_id, "home_currency": p.home_currency, "current_balance": float(p.current_available_balance)} for p in orchestrator.loader.financial_profiles]

@app.get("/users/{user_id}")
def get_user(user_id: str):
    orchestrator = Orchestrator.get_instance()
    profile = orchestrator.get_user(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
        
    events = [e for e in orchestrator.loader.financial_events if e.user_id == user_id]
    active_events = len([e for e in events if e.status not in ('cancelled', 'settled')])
    
    return {
        "user_id": profile.user_id,
        "home_currency": profile.home_currency,
        "current_balance": float(profile.current_available_balance),
        "minimum_balance": float(profile.minimum_balance_to_keep),
        "priorities": profile.financial_priorities,
        "active_events_count": active_events
    }

@app.get("/requests")
def list_requests():
    orchestrator = Orchestrator.get_instance()
    return [{"request_id": r.request_id, "user_id": r.user_id, "request_date": str(r.request_date), "requested_amount": float(r.requested_amount), "request_text": r.request_text} for r in orchestrator.loader.requests]

@app.get("/users/{user_id}/purchases")
def get_user_purchases(user_id: str):
    orchestrator = Orchestrator.get_instance()
    purchases = [r for r in orchestrator.loader.requests if r.user_id == user_id]
    return [{"request_id": r.request_id, "request_date": str(r.request_date), "requested_amount": float(r.requested_amount), "request_text": r.request_text} for r in purchases]

class OnboardingInput(BaseModel):
    user_id: str
    current_balance: float
    minimum_balance: float
    home_currency: str
    income: List[dict]
    recurring_expenses: List[dict]
    obligations: List[dict]
    payment_preferences: List[str]

@app.post("/users/onboarding")
def create_user_profile(body: OnboardingInput):
    import uuid
    from datetime import date
    from decimal import Decimal
    from app.models.schemas import FinancialProfile, FinancialEvent
    
    orchestrator = Orchestrator.get_instance()
    
    profile = FinancialProfile(
        user_id=body.user_id,
        home_currency=body.home_currency,
        current_available_balance=Decimal(str(body.current_balance)),
        minimum_balance_to_keep=Decimal(str(body.minimum_balance)),
        financial_priorities=[],
        expense_categories_to_protect=[],
        expense_categories_user_is_willing_to_reduce=[],
        expense_categories_user_is_willing_to_stop=[],
        payment_methods_user_will_consider=body.payment_preferences,
        max_installment_months=None
    )
    orchestrator.loader.financial_profiles.append(profile)
    
    today = date.today()
    
    # Process Income
    for inc in body.income:
        orchestrator.loader.financial_events.append(FinancialEvent(
            event_id=f"EVT-{str(uuid.uuid4())[:8]}",
            user_id=body.user_id,
            event_type="recurring_income" if inc.get('frequency') else "income",
            description=inc.get('source', 'Income'),
            category="income",
            direction="inbound",
            amount=Decimal(str(inc['amount'])),
            currency=body.home_currency,
            event_date=today,
            settlement_date=None,
            status="expected",
            linked_event_id=None,
            flexibility="fixed",
            minimum_allowed_amount=Decimal(str(inc['amount']))
        ))
        
    # Process Expenses
    for exp in body.recurring_expenses:
        orchestrator.loader.financial_events.append(FinancialEvent(
            event_id=f"EVT-{str(uuid.uuid4())[:8]}",
            user_id=body.user_id,
            event_type="recurring_expense",
            description=exp.get('name', 'Expense'),
            category="expense",
            direction="outbound",
            amount=Decimal(str(exp['amount'])),
            currency=body.home_currency,
            event_date=today,
            settlement_date=None,
            status="expected",
            linked_event_id=None,
            flexibility=exp.get('flexibility', 'fixed'),
            minimum_allowed_amount=Decimal(str(exp['amount']))
        ))
        
    # Process Obligations
    for obl in body.obligations:
        try:
            evt_date = date.fromisoformat(obl['date'])
        except:
            evt_date = today
        orchestrator.loader.financial_events.append(FinancialEvent(
            event_id=f"EVT-{str(uuid.uuid4())[:8]}",
            user_id=body.user_id,
            event_type="one_time_expense",
            description=obl.get('description', 'Obligation'),
            category="expense",
            direction="outbound",
            amount=Decimal(str(obl['amount'])),
            currency=body.home_currency,
            event_date=evt_date,
            settlement_date=None,
            status="expected",
            linked_event_id=None,
            flexibility="fixed",
            minimum_allowed_amount=Decimal(str(obl['amount']))
        ))
        
    return {"status": "success", "user_id": body.user_id}

@app.get("/requests/{request_id}")
def get_request(request_id: str):
    orchestrator = Orchestrator.get_instance()
    req = orchestrator.get_request(request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
        
    return {
        "request_id": req.request_id,
        "user_id": req.user_id,
        "request_date": str(req.request_date),
        "requested_amount": float(req.requested_amount),
        "desired_completion_date": str(req.desired_completion_date) if req.desired_completion_date else None,
        "allows_partial_payment": req.allows_partial_payment,
        "request_text": req.request_text
    }

class CreateRequestInput(BaseModel):
    user_id: str
    request_text: str
    requested_amount: float
    currency: str
    desired_completion_date: str
    request_type: str
    allows_partial_payment: bool
    payment_methods: List[str]

@app.post("/requests")
def create_request(body: CreateRequestInput):
    import uuid
    from datetime import date
    from decimal import Decimal
    from app.models.schemas import UserRequest
    
    orchestrator = Orchestrator.get_instance()
    
    # Basic validation
    if body.requested_amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be > 0")
        
    request_id = f"REQ-NEW-{str(uuid.uuid4())[:8]}"
    
    try:
        completion_date = date.fromisoformat(body.desired_completion_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
        
    new_req = UserRequest(
        request_id=request_id,
        user_id=body.user_id,
        request_date=date.today(),
        request_type=body.request_type,
        requested_amount=Decimal(str(body.requested_amount)),
        desired_completion_date=completion_date,
        allows_partial_payment=body.allows_partial_payment,
        request_text=body.request_text
    )
    
    orchestrator.loader.requests.append(new_req)
    
    from app.models.schemas import RequestPaymentOption
    for pm in body.payment_methods:
        opt_id = f"OPT-{str(uuid.uuid4())[:8]}"
        opt = RequestPaymentOption(
            payment_option_id=opt_id,
            request_id=request_id,
            payment_method=pm,
            payment_amount=Decimal(str(body.requested_amount)) if pm == 'full_payment' else Decimal("0"), # Dummy amounts for now except full
            number_of_payments=1 if pm == 'full_payment' else 2, # simplified
            first_payment_date=date.today(),
            payment_frequency_days=30 if pm != 'full_payment' else None,
            financing_fee=Decimal("0"),
            total_payable_amount=Decimal(str(body.requested_amount))
        )
        orchestrator.loader.request_payment_options.append(opt)
    
    return {"request_id": request_id}

@app.post("/requests/{request_id}/evaluate")
def evaluate_request_by_id(request_id: str):
    orchestrator = Orchestrator.get_instance()
    res = orchestrator.evaluate(request_id)
    if not res:
        raise HTTPException(status_code=404, detail="Request or User not found")
    
    out = res.copy()
    out.pop("trace", None)
    return out

class EvaluateInput(BaseModel):
    request_id: str

@app.post("/evaluate")
def evaluate_request_body(body: EvaluateInput):
    return evaluate_request_by_id(body.request_id)

class BatchEvaluateInput(BaseModel):
    request_ids: List[str]

@app.post("/evaluate/batch")
def evaluate_batch(body: BatchEvaluateInput):
    orchestrator = Orchestrator.get_instance()
    results = []
    failed = []
    
    for rid in body.request_ids:
        res = orchestrator.evaluate(rid)
        if res:
            out = res.copy()
            out.pop("trace", None)
            results.append(out)
        else:
            failed.append(rid)
            
    return {
        "completed": len(results),
        "failed": len(failed),
        "results": results
    }

@app.get("/requests/{request_id}/evidence")
def get_evidence(request_id: str):
    orchestrator = Orchestrator.get_instance()
    req = orchestrator.get_request(request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
        
    user_facts = [f for f in orchestrator.all_facts if f.user_id == req.user_id]
    
    return [
        {
            "fact_id": f.fact_id,
            "source_type": f.source_type,
            "source_id": f.source_id,
            "fact_type": f.fact_type,
            "related_event_id": f.related_event_id,
            "values": f.values,
            "effective_date": str(f.effective_date) if f.effective_date else None,
            "confidence": f.confidence,
            "extraction_method": f.extraction_method
        } for f in user_facts
    ]

@app.get("/requests/{request_id}/trace")
def get_trace(request_id: str):
    orchestrator = Orchestrator.get_instance()
    res = orchestrator.evaluate(request_id)
    if not res:
        raise HTTPException(status_code=404, detail="Request not found")
        
    trace = res.get("trace")
    if not trace:
        return {}
        
    # Serialize trace
    return {
        "checkpoints": [
            {
                "date": str(c.date),
                "balance_start": float(c.balance_start),
                "balance_end": float(c.balance_end),
                "min_balance": float(c.min_balance) if c.min_balance is not None else None,
                "events_applied": c.events_applied
            } for c in trace.checkpoints
        ],
        "violation_date": str(trace.violation_date) if trace.violation_date else None,
        "violation_event": trace.violation_event,
        "min_balance": float(trace.min_balance) if trace.min_balance is not None else None
    }

@app.get("/usage")
def get_usage():
    orchestrator = Orchestrator.get_instance()
    
    logs = getattr(orchestrator.extractor, "logs", [])
    total_calls = len(logs)
    total_in = sum(l.usage.input_tokens for l in logs) if logs else 0
    total_out = sum(l.usage.output_tokens for l in logs) if logs else 0
    total_cost = sum(l.usage.estimated_cost_usd for l in logs) if logs else 0.0
    
    return {
        "total_llm_calls": total_calls,
        "cache_hits": 0,
        "cache_misses": 0,
        "input_tokens": total_in,
        "output_tokens": total_out,
        "total_tokens": total_in + total_out,
        "estimated_cost": total_cost,
        "image_calls": 0,
        "fast_path_count": 0
    }
