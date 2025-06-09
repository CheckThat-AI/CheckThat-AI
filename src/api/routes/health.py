from fastapi import APIRouter
from ..models.responses import HealthCheck
from ..core.config import settings

router = APIRouter(tags=["health"])

@router.get("/", response_model=HealthCheck)
async def root():
    """
    Root endpoint that returns the API health status
    """
    return HealthCheck(status="healthy", version=settings.version)

@router.get("/health", response_model=HealthCheck)
async def health_check():
    """
    Health check endpoint
    """
    return HealthCheck(status="healthy", version=settings.version) 