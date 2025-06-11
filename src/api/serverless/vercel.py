from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import os
import sys
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from src.utils.get_model_response import get_model_response
from src.utils.prompts import sys_prompt, few_shot_CoT_prompt
from src.api.models.requests import ChatRequest

app = FastAPI()

@app.post("/api/chat")
async def chat_interface(request: ChatRequest):
    """
    Serverless chat endpoint - no WebSocket support
    Returns complete response instead of streaming
    """
    try:
        # Validate model
        valid_models = [
            "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            "claude-3.7-sonnet-latest", 
            "gpt-4o-2024-11-20",
            "gpt-4.1-2025-04-14",
            "gpt-4.1-nano-2025-04-14",
            "gemini-2.5-pro-preview-05-06",
            "gemini-2.5-flash-preview-04-17",
            "grok-3-latest"
        ]
        
        if request.model not in valid_models:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid model. Must be one of: {', '.join(valid_models)}"
            )
        
        # Set API key if provided
        api_provider = get_api_provider(request.model)
        if request.api_key:
            os.environ[f"{api_provider}_API_KEY"] = request.api_key

        # Get complete response (no streaming in serverless)
        response_chunks = []
        for chunk in get_model_response(
            model=request.model,
            user_prompt=f"{few_shot_CoT_prompt}\n\n{request.user_query}",
            sys_prompt=sys_prompt,
            gen_type="chat"
        ):
            response_chunks.append(chunk)
        
        complete_response = "".join(response_chunks)
        return {"response": complete_response, "model": request.model}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_api_provider(model: str) -> str:
    """Determine API provider from model name"""
    if model in ["gpt-4o-2024-11-20", "gpt-4.1-2025-04-14", "gpt-4.1-nano-2025-04-14"]:
        return "OPENAI"
    elif model == "grok-3-latest":
        return "GROK" 
    elif model == "claude-3.7-sonnet-latest":
        return "ANTHROPIC"
    elif model in ["gemini-2.5-pro-preview-05-06", "gemini-2.5-flash-preview-04-17"]:
        return "GEMINI"
    else:
        return "TOGETHER"

# For Vercel deployment
handler = app 