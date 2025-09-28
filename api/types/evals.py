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
class StaticEvaluation(BaseModel):
    """
    Pydantic model for Evaluating initial claims in the refinement process 
    using a static criteria and evaluation steps.
    """
    criteria: str = Field(description="The criteria to evaluate the claim against")
    evaluation_steps: List[str] = Field(description="The steps to evaluate the claim")
    
STATIC_EVAL_SPECS = StaticEvaluation(
    criteria="""Evaluate the normalized claim against the following criteria: Verifiability and Self-Containment, Claim Centrality and Extraction Quality,
    Conciseness and Clarity, Check-Worthiness Alignment, and Factual Consistency""",
    
    evaluation_steps=[
        # Verifiability and Self-Containment
        "Check if the claim contains verifiable factual assertions that can be independently checked",
        "Check if the claim is self-contained without requiring additional context from the original post",
        
        # Claim Centrality and Extraction Quality
        "Check if the normalized claim captures the central assertion from the source text while removing extraneous information",
        "Check if the claim represents the core factual assertion that requires fact-checking, not peripheral details",
        
        # Conciseness and Clarity
        "Check if the claim is presented in a straightforward, concise manner that fact-checkers can easily process",
        "Check if the claim is significantly shorter than source posts while preserving essential meaning",
        
        # Check-Worthiness Alignment
        "Check if the normalized claim meets check-worthiness standards for fact-verification",
        "Check if the claim has general public interest, potential for harm, and likelihood of being false",
        
        # Factual Consistency
        "Check if the normalized claim is factually consistent with the source material without hallucinations or distortions",
        "Check if the claim accurately reflects the original assertion without introducing new information",
    ]
)


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