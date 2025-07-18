import os
import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

# Import from the utils folder that's now inside the api folder
from ..utils.get_model_response import get_model_response
from ..utils.prompts import sys_prompt, few_shot_CoT_prompt, chat_guide
from ..models.requests import ChatRequest

router = APIRouter(prefix="/chat", tags=["chat"])

VALID_MODELS = [
    "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    "claude-sonnet-4-20250514",
    "claude-opus-4-20250514",
    "gpt-4o-2024-11-20",
    "gpt-4.1-2025-04-14",
    "gpt-4.1-nano-2025-04-14",
    "gemini-2.5-pro-preview-05-06",
    "gemini-2.5-flash-preview-04-17",
    "grok-3",
    "grok-3-mini",
    "grok-3-mini-fast"
]

def get_api_provider(model: str) -> str:
    """Determine the API provider based on the model"""
    if model in ["gpt-4o-2024-11-20", "gpt-4.1-2025-04-14", "gpt-4.1-nano-2025-04-14"]:
        return "OPENAI"
    elif model in ["grok-3-mini"]:
        return "GROK"
    elif model in ["claude-sonnet-4-20250514", "claude-opus-4-20250514"]:
        return "ANTHROPIC"
    elif model in ["gemini-2.5-pro-preview-05-06", "gemini-2.5-flash-preview-04-17"]:
        return "GEMINI"
    else:
        return "TOGETHER"

@router.post("")
async def chat_interface(request: ChatRequest):
    """
    Endpoint to normalize a single claim from the user provided text
    """
    try:
        print("Requested model:", request.model)

        if request.model not in VALID_MODELS:
            print(f"Invalid model: {request.model}")
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid model. Must be one of: {', '.join(VALID_MODELS)}"
            )
        
        api_provider = get_api_provider(request.model)
        
        if request.api_key:
            os.environ[f"{api_provider}_API_KEY"] = request.api_key
        
        def stream_response():
            for chunk in get_model_response(
                model=request.model,
                user_prompt=f"{few_shot_CoT_prompt}\n{chat_guide}\n\n{request.user_query}",
                sys_prompt=sys_prompt,
                gen_type="chat"
            ):
                yield chunk

        return StreamingResponse(stream_response(), media_type="text/plain")

    except Exception as e:
        print("Error in chat_interface:", str(e))
        raise HTTPException(status_code=500, detail=str(e)) 