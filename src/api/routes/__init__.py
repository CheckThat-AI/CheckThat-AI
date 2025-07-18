from fastapi import APIRouter
from . import health, chat, extraction, eval, session, auth

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(health.router)
api_router.include_router(chat.router)
api_router.include_router(extraction.router)
api_router.include_router(eval.router)
api_router.include_router(session.router)
api_router.include_router(auth.router) 