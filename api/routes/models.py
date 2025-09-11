from fastapi import APIRouter
from ..utils.models import models_list
router = APIRouter(tags=["models"])

@router.get("/models")
async def list_models():
    return models_list

@router.get("/v1/models")
async def list_models_v1():
    return models_list