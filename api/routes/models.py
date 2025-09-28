from fastapi import APIRouter
from .._types import models_list
router = APIRouter(tags=["models"])

@router.get("/v1/models")
async def list_models_v1():
    return models_list