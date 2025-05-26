import os
import json
from together import Together
from typing import Any
from .gpt import get_gpt_response
from .grok import get_grok_response
from .llama import get_llama_response
from .gemini import get_gemini_response
from .claude import get_claude_response

def get_chatbot_response(model: str, sys_prompt: str, user_prompt: str) -> str:

    ERROR_MESSAGE = "Exception in Chatbot's response: "
    output_type = None
    gen_type = "chat"
    response: str
    try:
        if model in ["gpt-4o-2024-11-20", "gpt-4.1-2025-04-14", "gpt-4.1-nano-2025-04-14", "grok-3-latest"]:
            response = get_gpt_response(model, sys_prompt, user_prompt, output_type, gen_type)

        elif model == "grok-3-latest":
            response = get_grok_response(model, sys_prompt, user_prompt, output_type, gen_type)
                    
        elif model == "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free":
            print("calling llama for a response")
            response = get_llama_response(model, sys_prompt, user_prompt, output_type, gen_type)
        
        elif model in ["gemini-2.5-pro-preview-05-06", "gemini-2.5-flash-preview-04-17"]:
            response = get_gemini_response(model, sys_prompt, user_prompt, output_type, gen_type)
        else:
                response = get_claude_response(model, sys_prompt, user_prompt, output_type, gen_type)

    except Exception as e:
        print(f"{ERROR_MESSAGE} {e}")
        response = "None"

    return response
