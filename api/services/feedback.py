from typing import Union, Type
from .claim_norm import ClaimNorm
from schemas.feedback import Feedback
from utils.anthropic import AnthropicModel
from utils.gemini import GeminiModel
from utils.openai import OpenAIModel
from utils.xai import xAIModel
from utils.LLMRouter import LLMRouter
from utils.llms import OPENAI_MODELS, xAI_MODELS, TOGETHER_MODELS, ANTHROPIC_MODELS, GEMINI_MODELS

class Feedback:
    def __init__(self, model: Union[OpenAIModel, xAIModel, AnthropicModel, GeminiModel]):
        self.model = model
        
    def get_feedback(self, user_prompt: str, sys_prompt: str, response_type: Type[Feedback]]):
        return self.model.generate_structured_response(sys_prompt, user_prompt, response_type)