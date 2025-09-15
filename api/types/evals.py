from pydantic import BaseModel, Field
from typing import List, Dict

class EvaluationReport(BaseModel):
    """
    Represents an evaluation report for post-normalization quality audits.
    This will be populated when evaluation features are implemented.
    """
    metrics_used: List[str] = Field(default_factory=list, description="The evaluation metrics that were applied")
    scores: Dict[str, float] = Field(default_factory=dict, description="Scores for each metric (0.0 to 1.0)")
    detailed_results: Dict[str, Dict] = Field(default_factory=dict, description="Detailed results for each metric")
    timestamp: str = Field(default="", description="ISO timestamp when the evaluation was performed")
    model_info: Dict[str, str] = Field(default_factory=dict, description="Information about the model used")


# Placeholder models for future implementation
class ClaimRefinementService:
    """
    Placeholder for claim refinement service.
    Will implement claim normalization algorithms.
    """
    pass


class EvaluationService:
    """
    Placeholder for evaluation service.
    Will implement quality evaluation metrics.
    """
    pass


class ReportStorageService:
    """
    Placeholder for report storage service.
    Will implement cloud storage and local file management.
    """
    pass
