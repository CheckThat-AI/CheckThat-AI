import os
import json
from typing import Any, Dict, List
from pydantic import BaseModel, Field
from openai import OpenAI
from together import Together
from google import genai
from google.genai import types
from .gpt import get_gpt_response
from .grok import get_grok_response
from .llama import get_llama_response
from .gemini import get_gemini_response

class NormalizedClaim(BaseModel):
    claim: str = Field(description="A normalized claim extracted from the noisy input text.")

class Feedback(BaseModel):
    verifiability: List[str] = Field(description="Feedback and Score for verifiability (0-10 scale)")
    false_likelihood: List[str] = Field(description="Feedback and Score for likelihood of being false (0-10 scale)")
    public_interest: List[str] = Field(description="Feedback and Score for public interest (0-10 scale)")
    potential_harm: List[str] = Field(description="Feedback and Score for potential harm (0-10 scale)")
    check_worthiness: List[str] = Field(description="Feedback and Score for check-worthiness (0-10 scale)")
    

def get_model_response(model:str, user_prompt:str, sys_prompt:str, gen_type:str)->str:
    """ This function takes a user prompt and a system prompt, and returns the generated response of the model using OpenAI's API.
    
    Args:
        user_prompt (str): The user's input prompt with the task query.
        sys_prompt (str): The system prompt to guide the model's response.

    Returns:
        str: The generated response from the model.
    
    """
    assert isinstance(user_prompt, str), "user_prompt must be a string"
    assert isinstance(sys_prompt, str), "sys_prompt must be a string"
    assert gen_type in ("feedback", "init", "refine"), f"gen_type must be either 'feedback' or 'init' or 'refine'; got {gen_type}"
    
    if gen_type == "feedback":
        output_type = Feedback
    else:
        output_type = NormalizedClaim
    
    generated_claim: str = "None"
     
    if model in ["gpt-4o-2024-11-20", "gpt-4.1-2025-04-14", "gpt-4.1-nano-2025-04-14", "grok-3-latest"]:
        
        generated_claim = get_gpt_response(sys_prompt, user_prompt, output_type, gen_type)

    elif model == "grok-3-latest":
        
        generated_claim = get_grok_response(sys_prompt, user_prompt, output_type, gen_type)
             
    elif model == "meta-llama/Llama-3.3-70B-Instruct-Turbo-Fre":
        
        generated_claim = get_llama_response(sys_prompt, user_prompt, output_type, gen_type)
        
    elif model in ["gemini-2.5-pro-preview-05-06", "gemini-2.5-flash-preview-04-17"]:
        
        generated_claim = get_gemini_response(sys_prompt, user_prompt, output_type, gen_type)
            
    #print(f"Model: {model}, Response: {generated_claim}")
    return generated_claim