from fastapi import APIRouter
from . import health, chat, extraction, metrics

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(health.router)
api_router.include_router(chat.router)
api_router.include_router(extraction.router)
api_router.include_router(metrics.router) 