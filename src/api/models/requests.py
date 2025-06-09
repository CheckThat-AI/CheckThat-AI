from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ChatRequest(BaseModel):
    user_query: str
    model: str
    api_key: Optional[str] = None

class EvalRequest(BaseModel):
    model: str
    prompt_style: str
    refine_iterations: int = 0
    eval_method: Optional[str] = None
    custom_prompt: Optional[str] = None
    api_key: Optional[str] = None
    cross_refine_model: Optional[str] = None

class EvaluationStartRequest(BaseModel):
    models: List[str]
    prompt_styles: List[str]
    file_data: Dict[str, str]  # name and content
    self_refine_iterations: int = 0
    eval_method: Optional[str] = None
    custom_prompt: Optional[str] = None
    api_keys: Dict[str, str] = {}
    cross_refine_model: Optional[str] = None
    field_mapping: Optional[Dict[str, Optional[str]]] = None
    eval_metric: Optional[str] = None

class WebSocketMessage(BaseModel):
    type: str
    data: Optional[Dict[str, Any]] = None 