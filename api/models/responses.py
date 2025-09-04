from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class RootResponse(BaseModel):
    message: str
    version: str

class HealthCheck(BaseModel):
    status: str
    version: str

class ChatResponse(BaseModel):
    normalized_claim: str
    model: str
    prompt_style: str
    meteor_score: float

class EvaluationResponse(BaseModel):
    success: bool
    message: str
    id: Optional[str] = None

class ProgressUpdate(BaseModel):
    type: str  # "progress", "log", "status", "error", "complete"
    data: Dict[str, Any]

class EvaluationComplete(BaseModel):
    message: str
    scores: Dict[str, float]

class MetricCalculationResponse(BaseModel):
    metric_type: str
    scores: List[float]
    execution_time: float
    success: bool
    detailed_results: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None

class BatchMetricResponse(BaseModel):
    results: Dict[str, MetricCalculationResponse]
    total_execution_time: float
    success: bool
    failed_metrics: Optional[List[str]] = None

class DeepEvalResponse(BaseModel):
    """Response for DeepEval dataset creation and evaluation"""
    success: bool
    message: str
    # Dataset information
    dataset_saved: bool
    dataset_location: Optional[str] = None  # Cloud alias or local path
    test_case_count: int
    dataset_reused: bool = False  # Whether an existing dataset was reused
    # Evaluation results
    evaluation_results: Optional[Dict[str, Any]] = None
    execution_time: float
    # Cloud information
    cloud_url: Optional[str] = None  # URL to view results on Confident AI cloud
    # Error information
    error_details: Optional[str] = None
    # File tracking
    file_hash: Optional[str] = None  # Hash of the file used for this evaluation

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None 