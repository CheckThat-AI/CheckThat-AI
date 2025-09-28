from typing import List
from pydantic import BaseModel, Field

OPENAI_MODELS = ["gpt-5-2025-08-07", "gpt-5-nano-2025-08-07", "o3-2025-04-16", "o4-mini-2025-04-16"]
OPENAI_MODEL_LABELS = ["GPT-5", "GPT-5 nano", "o3", "o4-mini"]

xAI_MODELS =  ["grok-3", "grok-4-0709", "grok-3-mini"]
xAI_MODEL_LABELS = ["Grok 3", "Grok 4", "Grok 3 Mini"]

TOGETHER_MODELS = ["meta-llama/Llama-3.3-70B-Instruct-Turbo-Free", "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free"]
TOGETHER_MODEL_LABELS = ["Llama 3.3 70B", "DeepSeek R1 Distill Llama 70B"]

ANTHROPIC_MODELS = ["claude-sonnet-4-20250514", "claude-opus-4-1-20250805"]
ANTHROPIC_MODEL_LABELS = ["Claude Sonnet 4", "Claude Opus 4.1"]

GEMINI_MODELS = ["gemini-2.5-pro", "gemini-2.5-flash"]
GEMINI_MODEL_LABELS = ["Gemini 2.5 Pro", "Gemini 2.5 Flash"]

class ModelFields(BaseModel):
    name: str = Field(description="The name of the model")
    model_id: str = Field(description="The model id")
    
    
class ModelListFields(BaseModel):
    provider: str = Field(description="The provider of the model")
    available_models: List[ModelFields] = Field(description="The models supported by the provider")
    
class Models(BaseModel):
    models_list: List[ModelListFields] = Field(description="The models supported by the provider")

models_list = Models(
    models_list=[
        ModelListFields(provider="OpenAI", available_models=[ModelFields(name=name, model_id=model_id) for name, model_id in zip(OPENAI_MODEL_LABELS, OPENAI_MODELS)]),
        ModelListFields(provider="Anthropic", available_models=[ModelFields(name=name, model_id=model_id) for name, model_id in zip(ANTHROPIC_MODEL_LABELS, ANTHROPIC_MODELS)]),
        ModelListFields(provider="Gemini", available_models=[ModelFields(name=name, model_id=model_id) for name, model_id in zip(GEMINI_MODEL_LABELS, GEMINI_MODELS)]), 
        ModelListFields(provider="xAI", available_models=[ModelFields(name=name, model_id=model_id) for name, model_id in zip(xAI_MODEL_LABELS, xAI_MODELS)]),
        ModelListFields(provider="Together AI", available_models=[ModelFields(name=name, model_id=model_id) for name, model_id in zip(TOGETHER_MODEL_LABELS, TOGETHER_MODELS)]),   
    ]
)


STRUCTURED_OUTPUT_SUPPORTED_MODELS = [
    # OpenAI models
    "gpt-5-2025-08-07", "gpt-5-nano-2025-08-07", "o3-2025-04-16", "o4-mini-2025-04-16",
    "gpt-4o-2024-08-06", "gpt-4o-mini-2024-07-18", "gpt-4o-2024-11-20",
    "gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-4-turbo",
    # Gemini models
    "gemini-2.5-pro", "gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash",
    # xAI models (Groq supports structured outputs)
    "grok-3", "grok-4-0709", "grok-3-mini",
    # Together AI models (some support structured outputs)
    "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    # Anthropic models (limited structured output support)
    "claude-sonnet-4-20250514"
]