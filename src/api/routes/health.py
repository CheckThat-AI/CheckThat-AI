from fastapi import APIRouter
from ..models.responses import HealthCheck, RootResponse
from ..core.config import settings

router = APIRouter(tags=["health"])

@router.get("/", response_model=RootResponse)
async def root():
    """
    Root endpoint that returns the API health status
    """
    return RootResponse(message="This is the ClaimNorm backend root API endpoint. Please use the /health endpoint to check the health of the API. Visit /docs for the API documentation.", version=settings.version)

@router.get("/health", response_model=HealthCheck)
async def health_check():
    """
    Health check endpoint
    """
    return HealthCheck(status="healthy", version=settings.version) 