from pydantic import BaseModel, Field
from typing import List

class NormalizedClaim(BaseModel):
    claim: str = Field(description="A normalized claim extracted from the noisy input text.")