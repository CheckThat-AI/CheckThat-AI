from pydantic import BaseModel
from typing import Optional, Dict, Any

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

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None 