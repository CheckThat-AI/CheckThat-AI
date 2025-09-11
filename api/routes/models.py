from fastapi import APIRouter
from ..utils.models import models_list
router = APIRouter(prefix="/v1", tags=["models"])

@router.get("/models")
async def list_models():
    return models_list