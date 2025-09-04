from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .rate_limiter import rate_limit_middleware

def setup_middleware(app: FastAPI) -> None:
    """Configure middleware for the FastAPI application"""
    
    # Add rate limiting middleware (CRITICAL for guest mode)
    app.middleware("http")(rate_limit_middleware)
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=[
            "Content-Type", 
            "Authorization", 
            "Accept", 
            "Accept-Language",
            "Cache-Control",
            "Origin",
            "X-Requested-With"
        ],  # Specific headers only for security
        expose_headers=["Content-Type", "Content-Length"]
    )