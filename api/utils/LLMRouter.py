import os
import sys
from pathlib import Path
from typing import Optional, Union

from .openai import OpenAIModel
from .xai import xAIModel
from .togetherAI import TogetherModel
from .gemini import GeminiModel
from .anthropic import AnthropicModel

from ..utils.models import OPENAI_MODELS, xAI_MODELS, TOGETHER_MODELS, ANTHROPIC_MODELS, GEMINI_MODELS

class LLMRouter:
    def __init__(self, model: str, api_key: Optional[str] = None):
        self.model = model
        if model in OPENAI_MODELS:
            self.api_provider = 'OPENAI'
        elif model in xAI_MODELS:
            self.api_provider = 'XAI'
        elif model in TOGETHER_MODELS:
            self.api_provider = 'TOGETHER'
        elif model in ANTHROPIC_MODELS:
            self.api_provider = 'ANTHROPIC'
        elif model in GEMINI_MODELS:
            self.api_provider = 'GEMINI'
        else:
            raise ValueError(f"Unsupported model: {model}")
        self.api_key = api_key
        
    def get_api_client(self)->Union[OpenAIModel, xAIModel, TogetherModel, AnthropicModel, GeminiModel]:
        if self.api_provider == 'OPENAI':
            return OpenAIModel(model=self.model, api_key=self.api_key)
        elif self.api_provider == 'XAI':
            return xAIModel(model=self.model, api_key=self.api_key)
        elif self.api_provider == 'TOGETHER':
            return TogetherModel(model=self.model, api_key=self.api_key)
        elif self.api_provider == 'ANTHROPIC':
            return AnthropicModel(model=self.model, api_key=self.api_key)
        elif self.api_provider == 'GEMINI':
            return GeminiModel(model=self.model, api_key=self.api_key)
        else:
            raise ValueError(f"Unsupported API provider: {self.api_provider}")
    