from fastapi import APIRouter
from . import health, chat
from .completions import router as completions_router
from .models import router as models_list

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(health.router)
api_router.include_router(chat.router)
api_router.include_router(completions_router)
api_router.include_router(models_list)