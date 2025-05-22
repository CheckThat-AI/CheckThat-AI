from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import pandas as pd
import os
from pathlib import Path
import sys

# Add the project root directory to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.utils.evaluate import start_evaluation

app = FastAPI(
    title="Claim Extraction and Normaization",
    description="API for the CLEF 2025 CheckThat Lab Task 2",
    version="1.0.0"
)

try:
    ENV_TYPE = os.getenv("ENV_TYPE")
except Exception as e:
    print(f"Error getting ENV_TYPE: {e}")
    
if ENV_TYPE == "dev":
    ORIGINS = ["http://localhost:5173"]
else:
    ORIGINS = ["https://nikhil-kadapala.github.io"]

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,  # Vite's default development server port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class HealthCheck(BaseModel):
    status: str
    version: str

class ErrorResponse(BaseModel):
    detail: str

class ClaimNormalizationRequest(BaseModel):
    model: str = "Llama"
    prompt_style: str = "Zero-shot"
    self_refine_iterations: int = 0
    custom_prompt: Optional[str] = None

class ClaimNormalizationResponse(BaseModel):
    meteor_score: float
    model: str
    prompt_style: str
    self_refine_iterations: int
    custom_prompt: Optional[str] = None

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

@app.post("/normalize-claims", response_model=ClaimNormalizationResponse)
async def normalize_claims(
    file: UploadFile = File(...),
    request: ClaimNormalizationRequest = None
):
    """
    Endpoint to normalize claims using the specified model and prompt style
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")
    
    try:
        # Read the uploaded CSV file
        df = pd.read_csv(file.file)
        
        # Get parameters from request or use defaults
        model = request.model if request else "Llama"
        prompt_style = request.prompt_style if request else "Zero-shot"
        self_refine_iterations = request.self_refine_iterations if request else 0
        custom_prompt = request.custom_prompt if request else None
        
        # Validate model and prompt style
        valid_models = ["Llama", "OpenAI", "Gemini", "Grok"]
        valid_prompts = ["Zero-shot", "Few-shot", "Zero-shot-CoT", "Few-shot-CoT"]
        
        if model not in valid_models:
            raise HTTPException(status_code=400, detail=f"Invalid model. Must be one of: {', '.join(valid_models)}")
        if prompt_style not in valid_prompts and not custom_prompt:
            raise HTTPException(status_code=400, detail=f"Invalid prompt style. Must be one of: {', '.join(valid_prompts)} or provide a custom prompt")
        
        # Run the evaluation
        meteor_score = start_evaluation(model, prompt_style, df, self_refine_iterations, custom_prompt)
        
        return ClaimNormalizationResponse(
            meteor_score=meteor_score,
            model=model,
            prompt_style=prompt_style,
            self_refine_iterations=self_refine_iterations,
            custom_prompt=custom_prompt
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 