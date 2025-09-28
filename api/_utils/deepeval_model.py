from deepeval.models import GPTModel, GeminiModel, AnthropicModel, GrokModel
from typing import Union, Optional
from .._types import OPENAI_MODELS, xAI_MODELS, ANTHROPIC_MODELS, GEMINI_MODELS

class DeepEvalModel:
    def __init__(
        self, 
        model: str, 
        api_key: str,
    ):
        self.model = model
        self.api_key = api_key
        
        # Determine API provider
        if model in OPENAI_MODELS:
            self.api_provider = 'OPENAI'
        elif model in xAI_MODELS:
            self.api_provider = 'XAI'
        elif model in ANTHROPIC_MODELS:
            self.api_provider = 'ANTHROPIC'
        elif model in GEMINI_MODELS:
            self.api_provider = 'GEMINI'
        else:
            # Default to OpenAI for unknown models
            self.api_provider = 'OPENAI'
    
    def getEvalModel(self)->Union[GPTModel, GeminiModel, AnthropicModel, GrokModel]:
        try:
            if self.api_provider == 'OPENAI':
                # Try with the original model name first
                try:
                    return GPTModel(model=self.model, _openai_api_key=self.api_key)
                except ValueError as e:
                    # If the model name is not recognized, try mapping to a supported one
                    if "gpt-4" in self.model.lower():
                        fallback_model = "gpt-4o"  # Use latest GPT-4 variant
                    elif "gpt-3.5" in self.model.lower():
                        fallback_model = "gpt-3.5-turbo"
                    else:
                        fallback_model = "gpt-4o"  # Default fallback
                    
                    return GPTModel(model=fallback_model, _openai_api_key=self.api_key)
                    
            elif self.api_provider == 'XAI':
                return GrokModel(model=self.model, api_key=self.api_key)
            elif self.api_provider == 'ANTHROPIC':
                return AnthropicModel(model=self.model, _anthropic_api_key=self.api_key)
            elif self.api_provider == 'GEMINI':
                return GeminiModel(model=self.model, api_key=self.api_key)
            else:
                raise ValueError(f"Unsupported API provider: {self.api_provider}")
        except Exception as e:
            # Last resort: create a basic GPT model for evaluation
            try:
                return GPTModel(model="gpt-4o", _openai_api_key=self.api_key)
            except:
                raise ValueError(f"Failed to create evaluation model: {str(e)}")