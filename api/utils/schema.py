from pydantic import BaseModel, Field
from typing import List

class NormalizedClaim(BaseModel):
    claim: str = Field(description="A normalized claim extracted from the noisy input text.")

class Feedback(BaseModel):
    verifiability: List[str] = Field(description="Feedback and Score for verifiability (0-10 scale)")
    false_likelihood: List[str] = Field(description="Feedback and Score for likelihood of being false (0-10 scale)")
    public_interest: List[str] = Field(description="Feedback and Score for public interest (0-10 scale)")
    potential_harm: List[str] = Field(description="Feedback and Score for potential harm (0-10 scale)")
    check_worthiness: List[str] = Field(description="Feedback and Score for check-worthiness (0-10 scale)")