# Buy or Wait - Financial Decision Engine

This repository contains the complete implementation of the deterministic financial affordability engine for evaluating user requests against their 90-day cash-flow projection, utilizing structured extraction on untrusted evidence (LLM parsing).

## Architecture

1. **Deterministic Core (Phases 1-4)**: Converts raw event CSV data into a conflict-resolved canonical timeline. Runs 90-day balance projections, exact lexicographic safety generation, and partial payment timelines mathematically without ML.
2. **Evidence Compiler (Phases 5-10)**: Uses the Gemini API strictly as an extraction compiler layer (`EvidenceExtractor`). It converts unstructured text/images into `EvidenceFact` JSON. The LLM NEVER determines affordability. Untrusted text is defended through strict Pydantic schemas. 
3. **Backend API (Phase 11)**: A FastAPI orchestrator wrapping the deterministic logic inside isolated POST endpoints ensuring canonical mutability constraints.
4. **Frontend Dashboard (Phase 12)**: A Razorpay-inspired React/Vite/Tailwind frontend that natively consumes the API payload to render decision traces, charts (Recharts), and usage telemetry.

## Quickstart

### 1. Setup Backend
```bash
# Ensure Python 3.9+
pip install -r requirements.txt
pip install fastapi uvicorn
```

### 2. Run Tests
Ensure all 19 deterministic/simulation regressions pass:
```bash
python -m unittest discover tests -v
python -m unittest tests.api.test_api -v
```

### 3. Generate Output (Phase 8/9 Batch Run)
Produces the final `output.csv` against the dataset offline:
```bash
python -m app.pipeline.runner
python -m app.pipeline.validator
```

### 4. Start API (Offline/Live Mode)
```bash
uvicorn app.api.app:app --reload
# Runs at http://localhost:8000
```
*Note: If `GEMINI_API_KEY` is omitted, the API defaults safely to Offline/DummyLLMClient mode.*

### 5. Start Frontend
```bash
cd frontend
npm install
npm run dev
# Runs at http://localhost:5173
```

## Environment Variables
Copy `.env.example` to `.env`:
```env
LLM_PROVIDER=gemini
LLM_MODEL=gemini-3.5-flash-lite
GEMINI_API_KEY=<your_api_key_here>
```

## Security & Tracing
- Prompt Injections are safely dropped by the LLM Schema Parser.
- Evidence amounts missing from images fallback to un-resolved states.
- Traces are securely returned via the `Decision.trace.checkpoints` object allowing the frontend to deterministically render charts without fabricating points.
