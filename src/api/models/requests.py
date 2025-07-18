from pydantic import BaseModel, field_validator
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

class ExtractionStartRequest(BaseModel):
    models: List[str]
    prompt_styles: List[str]
    file_data: Dict[str, str]  # name and content
    refine_iterations: int = 0
    eval_method: Optional[str] = None
    custom_prompt: Optional[str] = None
    api_keys: Dict[str, str] = {}
    cross_refine_model: Optional[str] = None
    field_mapping: Optional[Dict[str, Any]] = None
    eval_metric: Optional[str] = None

class MetricCalculationRequest(BaseModel):
    metric_type: str  # 'meteor', 'rouge', 'bleu', 'bert', 'cosine'
    # For direct calculation (when texts are provided)
    response_texts: Optional[List[str]] = None
    reference_texts: Optional[List[str]] = None
    # For session-based calculation (when texts are stored in evaluation context)
    session_id: Optional[str] = None
    evaluation_result_id: Optional[str] = None
    # Common parameters
    config: Optional[Dict[str, Any]] = None
    return_detailed: bool = False
    
    @field_validator('response_texts', 'reference_texts')
    @classmethod
    def validate_text_consistency(cls, v, info):
        # If we have session_id, texts are optional
        if info.data.get('session_id') or info.data.get('evaluation_result_id'):
            return v
        # If no session context, both texts must be provided
        if v is None and info.field_name in ['response_texts', 'reference_texts']:
            raise ValueError("Either provide session_id/evaluation_result_id OR both response_texts and reference_texts")
        return v

class SessionMetricRequest(BaseModel):
    """Simplified request for session-based metric calculation"""
    session_id: str
    metric_type: str
    config: Optional[Dict[str, Any]] = None
    return_detailed: bool = False

class BatchMetricRequest(BaseModel):
    metrics: List[str]  # Multiple metrics to calculate
    # For direct calculation
    response_texts: Optional[List[str]] = None
    reference_texts: Optional[List[str]] = None
    # For session-based calculation
    session_id: Optional[str] = None
    evaluation_result_id: Optional[str] = None
    # Common parameters
    configs: Optional[Dict[str, Dict[str, Any]]] = None  # Config per metric
    return_detailed: bool = False

class BatchSessionMetricRequest(BaseModel):
    """Simplified request for session-based batch metric calculation"""
    session_id: str
    metrics: List[str]
    configs: Optional[Dict[str, Dict[str, Any]]] = None
    return_detailed: bool = False

class DeepEvalRequest(BaseModel):
    """Request for DeepEval dataset creation and evaluation"""
    session_id: str
    metric_type: str  # 'faithfulness', 'hallucination', etc.
    # Model configuration for evaluation
    model_provider: str  # 'openai', 'gemini', 'anthropic'
    model_name: str
    api_key: str
    # Confident AI cloud configuration (optional)
    confident_api_key: Optional[str] = None
    dataset_alias: str = "MyDataset"
    # Metric configuration
    threshold: float = 0.7
    include_reason: bool = True
    strict_mode: bool = False
    # Dataset configuration
    save_to_cloud: bool = False
    local_directory: str = "./deepeval-test-dataset"
    # Session management
    store_api_keys: bool = True  # Whether to store API keys for session duration

class WebSocketMessage(BaseModel):
    type: str
    data: Optional[Dict[str, Any]] = None 