import os
import json
import urllib.request
from typing import List, Dict, Any, Optional, Tuple
from app.models.state import EvidenceFact
from app.evidence.models import TokenUsage
from app.evidence.llm_client import LLMClient

class GeminiLLMClient(LLMClient):
    def __init__(self, api_key: str, model_name: str = "gemini-3.5-flash-lite"):
        self.api_key = api_key
        self.model_name = os.environ.get("LLM_MODEL", model_name)
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        
    def _call_api(self, prompt: str) -> Tuple[Dict[str, Any], TokenUsage]:
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "responseMimeType": "application/json"
            }
        }
        req = urllib.request.Request(self.base_url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req) as response:
                resp_json = json.loads(response.read().decode('utf-8'))
                
                text_response = resp_json['candidates'][0]['content']['parts'][0]['text']
                usage = resp_json.get('usageMetadata', {})
                
                input_tokens = usage.get('promptTokenCount', 0)
                output_tokens = usage.get('candidatesTokenCount', 0)
                
                try:
                    parsed = json.loads(text_response)
                except json.JSONDecodeError:
                    parsed = {"fact_type": "irrelevant", "confidence": 0.0}
                    
                # Very rough estimate $0.075 / 1M tokens
                est_cost = (input_tokens + output_tokens) * (0.075 / 1000000)
                
                return parsed, TokenUsage(input_tokens, output_tokens, input_tokens + output_tokens, est_cost)
        except Exception as e:
            return {"fact_type": "irrelevant", "confidence": 0.0}, TokenUsage()

    def extract_structured(self, prompt: str, text: str, schema: Dict) -> Tuple[Dict[str, Any], TokenUsage]:
        full_prompt = f"{prompt}\n\nSOURCE TEXT:\n{text}"
        return self._call_api(full_prompt)
        
    def extract_batch(self, prompt: str, texts: List[str], schema: Dict) -> Tuple[List[Dict[str, Any]], TokenUsage]:
        # For batching, we ask it to return a JSON array
        texts_str = "\n".join([f"ID_{i}: {t}" for i, t in enumerate(texts)])
        full_prompt = f"{prompt}\n\nInstead of a single JSON object, return a JSON array of objects, one for each source text in order.\n\nSOURCE TEXTS:\n{texts_str}"
        
        parsed, usage = self._call_api(full_prompt)
        if isinstance(parsed, list) and len(parsed) == len(texts):
            return parsed, usage
        else:
            # Fallback
            return [{"fact_type": "irrelevant", "confidence": 0.0} for _ in texts], usage
        
    def extract_image(self, prompt: str, image_path: str, schema: Dict) -> Tuple[Dict[str, Any], TokenUsage]:
        # Skipping actual image upload bytes for now without SDK
        return {"fact_type": "irrelevant", "confidence": 0.0}, TokenUsage()

