from fastapi import APIRouter
from . import health, chat, eval, auth, drive

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(health.router)
api_router.include_router(chat.router)
api_router.include_router(eval.router)
api_router.include_router(drive.router)
api_router.include_router(auth.router) 