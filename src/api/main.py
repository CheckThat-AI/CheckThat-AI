from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import uvicorn
import pandas as pd
import os
import sys
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.utils.get_model_response import get_model_response
from src.utils.prompts import sys_prompt, few_shot_CoT_prompt

app = FastAPI(
    title="Claim Extraction and Normaization",
    description="API for the CLEF 2025 CheckThat Lab Task 2",
    version="1.0.0"
)

try:
    ENV_TYPE = os.getenv("ENV_TYPE", "dev")  # Default to dev if not set
except Exception as e:
    print(f"Error getting ENV_TYPE: {e}")
    ENV_TYPE = "dev"  # Default to dev on error
    
if ENV_TYPE == "dev":
    ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
else:
    ORIGINS = ["https://nikhil-kadapala.github.io"]

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Pydantic models
class HealthCheck(BaseModel):
    status: str
    version: str

class ErrorResponse(BaseModel):
    detail: str

class ClaimNormalizationRequest(BaseModel):
    model: str = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Fre"
    prompt_style: str = "Zero-shot"
    self_refine_iterations: int = 0
    custom_prompt: Optional[str] = None

class ClaimNormalizationResponse(BaseModel):
    meteor_score: float
    model: str
    prompt_style: str
    self_refine_iterations: int
    custom_prompt: Optional[str] = None

class SingleClaimRequest(BaseModel):
    user_query: str
    model: str
    api_key: Optional[str] = None

class ChatResponse(BaseModel):
    normalizedClaim: str = Field(..., description="The normalized claim")

@app.get("/", response_model=HealthCheck)
async def root():
    """
    Root endpoint that returns the API health status
    """
    return HealthCheck(status="healthy", version="1.0.0")

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """
    Health check endpoint
    """
    return HealthCheck(status="healthy", version="1.0.0")

@app.post("/chat", response_model=ChatResponse)
async def normalize_single_claim(request: SingleClaimRequest):
    """
    Endpoint to normalize a single claim from the user provided text
    """
    try:
        print("Received request:", request.dict())

        valid_models = [
            "meta-llama/Llama-3.3-70B-Instruct-Turbo-Fre",
            "claude-3.7-sonnet-latest",
            "gpt-4o-2024-11-20",
            "gpt-4.1-2025-04-14",
            "gpt-4.1-nano-2025-04-14",
            "gemini-2.5-pro-preview-05-06",
            "gemini-2.5-flash-preview-04-17",
            "grok-3-latest"
        ]
        
        API_PROVIDER: Optional[str] = None
        
        if request.model not in valid_models:
            print(f"Invalid model: {request.model}")
            raise HTTPException(status_code=400, detail=f"Invalid model. Must be one of: {', '.join(valid_models)}")
        
        if request.model in ["gpt-4o-2024-11-20", "gpt-4.1-2025-04-14", "gpt-4.1-nano-2025-04-14", "grok-3-latest"]:
            API_PROVIDER = "OPENAI"
        elif request.model in ["claude-3.7-sonnet-latest"]:
            API_PROVIDER = "ANTHROPIC"
        elif request.model in ["gemini-2.5-pro-preview-05-06", "gemini-2.5-flash-preview-04-17"]:
            API_PROVIDER = "GEMINI"
        else:
            API_PROVIDER = "TOGETHER"
        
        print(f"Using API provider: {API_PROVIDER}")
        
        if request.api_key:
            print("Setting API key for provider")
            os.environ[f"{API_PROVIDER}_API_KEY"] = request.api_key

        print(f"Model: {request.model} \nUser Query: {request.user_query}")
        
        normalized_claim = get_model_response(
            model=request.model,
            user_prompt=request.user_query,
            sys_prompt="Few-shot-CoT",
            gen_type="init"
        )
        print("Normalized claim:", normalized_claim)
        return ChatResponse(normalizedClaim=normalized_claim)
        
    except Exception as e:
        print("Error in normalize_single_claim:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

