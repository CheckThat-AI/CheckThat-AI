from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings

def setup_middleware(app: FastAPI) -> None:
    """Configure middleware for the FastAPI application"""
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"]
    ) 