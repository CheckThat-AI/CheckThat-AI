import logging
import os
from fastapi import FastAPI
from .core.config import settings
from .core.middleware import setup_middleware
from .routes import api_router

# Configure logging based on environment
log_level = os.getenv("LOG_LEVEL", "INFO" if settings.env_type == "prod" else "DEBUG").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create FastAPI application
app = FastAPI(
    title=settings.title,
    description=settings.description,
    version=settings.version
)

# Setup middleware
setup_middleware(app)

# Include all API routes
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)