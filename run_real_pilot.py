import os
import json
import time
from app.models.schemas import Message, Image
from app.evidence.models import ExtractionConfig
from app.evidence.llm_client import ExtractionCache
from app.evidence.extractor import EvidenceExtractor
from app.evidence.gemini_client import GeminiLLMClient

def load_golden():
    with open('tests/fixtures/golden_evidence.json') as f:
        return json.load(f)

def run_real_pilot():
    print("--- PRE-FLIGHT COST CHECK ---")
    golden = load_golden()
    num_samples = len(golden)
    
    # Rough estimate: 500 input tokens, 50 output tokens per sample
    est_input = num_samples * 500
    est_output = num_samples * 50
    # Gemini 3.5 Flash Lite cost approximation
    est_cost = (est_input / 1_000_000) * 0.075 + (est_output / 1_000_000) * 0.30
    
    print(f"Pilot Size: {num_samples} samples")
    print(f"Estimated Input Tokens: {est_input}")
    print(f"Estimated Output Tokens: {est_output}")
    print(f"Estimated Cost: ${est_cost:.6f}")
    
    if est_cost > 1.0:
        print("Cost estimate too high, stopping.")
        return
        
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("WARN: GEMINI_API_KEY not found in environment. Cannot execute REAL LLM calls. Aborting live extraction.")
        
        report = f"""# Real Model Pilot Usage Report

## Metrics
- Provider: Gemini (REST API)
- Model: gemini-3.5-flash-lite
- Pilot Size: {num_samples}
- Live Calls: 0
- Cached Calls: 0
- Total Input Tokens: 0
- Total Output Tokens: 0
- Total Tokens: 0
- Total Estimated Cost: $0.00
- Fast-Path Effectiveness: 0%
- Extraction Accuracy: N/A (API Key missing)
- Image Accuracy: N/A
- Downstream Decision Changes: 0
- Failures: LLM Provider Unavailable

## Full-Dataset Cost Estimate
- Expected Calls: 25000 (Events)
- Expected Tokens: 13,750,000
- Expected Cost: ~$1.50
- Upper Bound: $5.00
"""
        with open('evaluation/real_model_pilot_report.md', 'w') as f:
            f.write(report)
            
        with open('evaluation/full_run_cost_estimate.md', 'w') as f:
            f.write(report)
            
        return
        
    print("Executing REAL pilot...")
    client = GeminiLLMClient(api_key=api_key)
    cache = ExtractionCache()
    config = ExtractionConfig(max_batch_size=2)
    extractor = EvidenceExtractor(client, cache, config)
    
    # ... logic for real extraction would go here ...
    
if __name__ == '__main__':
    run_real_pilot()
