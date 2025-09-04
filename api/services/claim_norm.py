import os
import sys
from pathlib import Path
from typing import Union, Type
from utils.anthropic import AnthropicModel
from utils.gemini import GeminiModel
from utils.openai import OpenAIModel
from utils.xai import xAIModel
from utils.LLMRouter import LLMRouter
from utils.llms import OPENAI_MODELS, xAI_MODELS, TOGETHER_MODELS, ANTHROPIC_MODELS, GEMINI_MODELS
from schemas.claims import NormalizedClaim
from schemas.feedback import Feedback

path = Path(__file__).parent.parent.parent
sys.path.append(str(path))

class ClaimNorm:
    def __init__(self, model: Union[OpenAIModel, xAIModel, AnthropicModel, GeminiModel]):
        self.model = model
        
    def normalize_claim(self, user_prompt: str, sys_prompt: str, response_type: Union[Type[NormalizedClaim], Type[Feedback]]):
        return self.model.generate_structured_response(sys_prompt, user_prompt, response_type)
        