from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List

@dataclass
class TokenUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0

@dataclass
class LLMOperationLog:
    timestamp: datetime
    provider: str
    model: str
    operation: str
    source_ids: List[str]
    batch_size: int
    usage: TokenUsage
    prompt_version: str
    cache_hit: bool
    
@dataclass
class ExtractionConfig:
    max_llm_calls: int = 50
    max_image_calls: int = 20
    max_retries: int = 2
    max_batch_size: int = 5
    max_context_tokens: int = 4000
    offline_mode: bool = True
