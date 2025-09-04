from typing import Union, Generator
from schemas.claims import NormalizedClaim
from schemas.feedback import Feedback
from .openai import OpenAIModel
from .xai import get_grok_structured_response, get_grok_streaming_response
from .togetherAI import get_llama_streaming_response, get_llama_structured_response
from .gemini import get_gemini_structured_response, get_gemini_streaming_response
from .anthropic import get_claude_structured_response, get_claude_streaming_response
from .LLMRouter import LLMRouter
from .llms import OPENAI_MODELS, xAI_MODELS, TOGETHER_MODELS, ANTHROPIC_MODELS, GEMINI_MODELS

def get_model_response(model:str, user_prompt:str, sys_prompt:str, gen_type:str)->Union[NormalizedClaim, Feedback, Generator[str, None, None]]:
    """ This function takes a user prompt and a system prompt, and returns the generated response of the model using OpenAI's API.
    
    Args:
        model (str): The model to use for generation.
        user_prompt (str): The user's input prompt with the task query.
        sys_prompt (str): The system prompt to guide the model's response.
        gen_type (str): The type of generation to perform. It can be "feedback", "init", "refine", or "chat".

    Returns:
        Union[NormalizedClaim, Feedback]: The generated response from the model.
    
    """
    assert isinstance(user_prompt, str), "user_prompt must be a string"
    assert isinstance(sys_prompt, str), "sys_prompt must be a string"
    assert gen_type in ("feedback", "init", "refine", "chat"), f"gen_type must be either 'feedback' or 'init' or 'refine' or 'chat'; got {gen_type}"
    
    if gen_type == "init" or gen_type == "refine":
        response_type = NormalizedClaim
    elif gen_type == "feedback":
        response_type = Feedback
    
    MODEL = LLMRouter(model=model).get_api_client()
    if gen_type == "chat":
        generated_claim = MODEL.generate_streaming_response(sys_prompt, user_prompt)
    elif gen_type in ["init", "refine", "feedback"]:
        generated_claim = MODEL.generate_structured_response(sys_prompt, user_prompt, response_type)
            
    return generated_claim