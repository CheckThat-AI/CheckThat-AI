from typing import Union, Generator
from .schema import NormalizedClaim, Feedback
from .openai import OpenAIModel
from .xai import get_grok_structured_response, get_grok_streaming_response
from .togetherAI import get_llama_streaming_response, get_llama_structured_response
from .gemini import get_gemini_structured_response, get_gemini_streaming_response
from .anthropic import get_claude_structured_response, get_claude_streaming_response

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
    
    if model in ["gpt-4o-2024-11-20", "gpt-4.1-2025-04-14", "gpt-4.1-nano-2025-04-14"]:
        MODEL = OpenAIModel(model=model)
        if gen_type == "chat":
            generated_claim = MODEL.generate_streaming_response(sys_prompt, user_prompt)
        elif gen_type in ["init", "refine", "feedback"]:
            generated_claim = MODEL.generate_structured_response(sys_prompt, user_prompt, response_type)
    elif model in ["grok-3","grok-3-mini", "grok-3-mini-fast"]:
        generated_claim = get_grok_streaming_response(model, sys_prompt, user_prompt) if gen_type == "chat" else get_grok_structured_response(model, sys_prompt, user_prompt, response_type)
             
    elif model in ["meta-llama/Llama-3.3-70B-Instruct-Turbo-Free", "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free"]:
        if gen_type == "chat":
            generated_claim = get_llama_streaming_response(model, sys_prompt, user_prompt)
        else:
            generated_claim = get_llama_structured_response(model, sys_prompt, user_prompt, response_type)

    elif model in ["gemini-2.5-pro-preview-05-06", "gemini-2.5-flash-preview-04-17"]:
        generated_claim = get_gemini_streaming_response(model, sys_prompt, user_prompt) if gen_type == "chat" else get_gemini_structured_response(model, sys_prompt, user_prompt, response_type)
        
    elif model in ["claude-sonnet-4-20250514", "claude-opus-4-20250514"]:
        generated_claim = get_claude_streaming_response(model, sys_prompt, user_prompt) if gen_type == "chat" else get_claude_structured_response(model, sys_prompt, user_prompt, response_type)
    
    else:
        raise ValueError(f"Unsupported model: {model}")
            
    return generated_claim