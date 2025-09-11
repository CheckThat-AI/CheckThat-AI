from fastapi import APIRouter
from ..models.responses import HealthCheck, RootResponse
from ..core.config import settings

router = APIRouter(tags=["health"])

@router.get("/", response_model=RootResponse)
async def root():
    """
    Root endpoint that returns the API health status
    """
    return RootResponse(message="This is the CheckThat AI backend root API endpoint. Visit https://www.github.com/nikhil-kadapala/checkthat-ai for the public API documentation.", version=settings.version)

@router.get("/health", response_model=HealthCheck)
async def health_check():
    """
    Health check endpoint
    """
    return HealthCheck(status="healthy", version=settings.version) 