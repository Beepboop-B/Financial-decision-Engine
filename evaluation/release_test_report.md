# Final Release Test Report

## 1. Core Financial Engine (Deterministic)
- **Execution Command:** `python -m unittest discover tests -v`
- **Result:** 19/19 Tests Passed
- **Coverage:** Canonical State Resolution, Conflict Overlays, Currency Normalization, Immutability, Simulation Limits, Lexicographic Plan Ranking, Spending Change Bounds.
- **Runtime:** `0.306s`

## 2. API Validation Layer
- **Execution Command:** `python -m unittest tests.api.test_api -v`
- **Result:** 10/10 Tests Passed
- **Coverage:** API Route Logic, Orchestrator Isolation, Mock Offline Switch, JSON Schema validation, Trace Generation.
- **Runtime:** `0.376s`

## 3. Offline Baseline Pipeline
- **Execution Command:** `python -m app.pipeline.validator`
- **Result:** OUTPUT VALIDATION PASSED.
- **Coverage:** Verified exact columns, correct row dimensions (250 entries), correct status bounds, and JSON structure formatting for payment plans and spending overrides.

## 4. Frontend Types/Build
- **Execution Command:** `npm run build`
- **Result:** Vite output bundles successfully generated.
- **Coverage:** React DOM typings, Recharts properties, Vite CSS token compilation.

## 5. Security Validations
- Secrets check completed cleanly.
- DummyLLMClient confirmed operating accurately when key bounds are absent.
- LLM Pydantic schemas correctly deflected structured injection logic in unit tests.
