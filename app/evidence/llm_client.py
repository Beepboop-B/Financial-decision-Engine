import json
from typing import List, Dict, Any, Optional, Tuple
from app.models.state import EvidenceFact
from app.evidence.models import TokenUsage

class LLMClient:
    def extract_structured(self, prompt: str, text: str, schema: Dict) -> Tuple[Dict[str, Any], TokenUsage]:
        raise NotImplementedError
        
    def extract_batch(self, prompt: str, texts: List[str], schema: Dict) -> Tuple[List[Dict[str, Any]], TokenUsage]:
        raise NotImplementedError
        
    def extract_image(self, prompt: str, image_path: str, schema: Dict) -> Tuple[Dict[str, Any], TokenUsage]:
        raise NotImplementedError

class DummyLLMClient(LLMClient):
    """
    Offline deterministic client for testing. 
    Reads from a predefined dictionary of mock responses.
    """
    def __init__(self, mock_responses: Dict[str, Any]):
        self.mock_responses = mock_responses
        self.calls_made = 0
        
    def _match(self, input_data: str) -> Dict[str, Any]:
        self.calls_made += 1
        for key, resp in self.mock_responses.items():
            if key in input_data:
                return resp
        # Default empty fallback matching schema
        return {"fact_type": "irrelevant", "confidence": 1.0}

    def extract_structured(self, prompt: str, text: str, schema: Dict) -> Tuple[Dict[str, Any], TokenUsage]:
        resp = self._match(text)
        return resp, TokenUsage(10, 10, 20, 0.0)
        
    def extract_batch(self, prompt: str, texts: List[str], schema: Dict) -> Tuple[List[Dict[str, Any]], TokenUsage]:
        resps = [self._match(t) for t in texts]
        return resps, TokenUsage(10*len(texts), 10*len(texts), 20*len(texts), 0.0)
        
    def extract_image(self, prompt: str, image_path: str, schema: Dict) -> Tuple[Dict[str, Any], TokenUsage]:
        resp = self._match(image_path)
        return resp, TokenUsage(50, 10, 60, 0.0)

class ExtractionCache:
    def __init__(self):
        self.store = {}
        
    def get(self, key: str) -> Optional[Any]:
        return self.store.get(key)
        
    def set(self, key: str, value: Any):
        self.store[key] = value
