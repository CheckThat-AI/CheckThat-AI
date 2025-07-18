"""
Session management routes for API key storage and cleanup.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

from ..utils.deepeval_session_manager import deepeval_session_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/session", tags=["session"])

class SessionApiKeyRequest(BaseModel):
    session_id: str
    confident_api_key: Optional[str] = None

class SessionModelApiKeysRequest(BaseModel):
    session_id: str
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    grok_api_key: Optional[str] = None

class SessionApiKeyResponse(BaseModel):
    success: bool
    message: str
    session_id: str
    has_api_key: bool

class SessionModelApiKeysResponse(BaseModel):
    success: bool
    message: str
    session_id: str
    api_keys: Dict[str, bool]  # Which keys are stored (without exposing values)

class SessionClearRequest(BaseModel):
    session_id: str

class SessionClearResponse(BaseModel):
    success: bool
    message: str
    session_id: str

@router.post("/api-key", response_model=SessionApiKeyResponse)
async def store_session_api_key(request: SessionApiKeyRequest):
    """
    Store or update the Confident AI API key for a session.
    
    Args:
        request: Session API key request
        
    Returns:
        Response indicating success/failure
    """
    try:
        deepeval_session_manager.set_session_api_key(
            request.session_id, 
            request.confident_api_key
        )
        
        return SessionApiKeyResponse(
            success=True,
            message="API key stored successfully",
            session_id=request.session_id,
            has_api_key=request.confident_api_key is not None
        )
        
    except Exception as e:
        logger.error(f"Failed to store API key for session {request.session_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to store API key: {str(e)}"
        )

@router.get("/api-key/{session_id}", response_model=SessionApiKeyResponse)
async def get_session_api_key_status(session_id: str):
    """
    Check if a session has an API key stored.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Response with API key status (without exposing the actual key)
    """
    try:
        has_api_key = deepeval_session_manager.is_session_authenticated(session_id)
        
        return SessionApiKeyResponse(
            success=True,
            message="API key status retrieved",
            session_id=session_id,
            has_api_key=has_api_key
        )
        
    except Exception as e:
        logger.error(f"Failed to get API key status for session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get API key status: {str(e)}"
        )

@router.delete("/clear/{session_id}", response_model=SessionClearResponse)
async def clear_session(session_id: str):
    """
    Clear all session data including API keys and DeepEval authentication.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Response indicating success/failure
    """
    try:
        deepeval_session_manager.clear_session(session_id)
        
        return SessionClearResponse(
            success=True,
            message="Session cleared successfully",
            session_id=session_id
        )
        
    except Exception as e:
        logger.error(f"Failed to clear session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear session: {str(e)}"
        )

@router.get("/dataset/{session_id}")
async def get_session_dataset_info(session_id: str):
    """
    Get dataset information for a session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Dataset information if available
    """
    try:
        dataset_info = deepeval_session_manager.get_session_dataset_info(session_id)
        
        if dataset_info:
            return {
                "success": True,
                "message": "Dataset info retrieved",
                "session_id": session_id,
                "dataset_info": dataset_info,
                "has_dataset": True
            }
        else:
            return {
                "success": True,
                "message": "No dataset found for session",
                "session_id": session_id,
                "dataset_info": None,
                "has_dataset": False
            }
        
    except Exception as e:
        logger.error(f"Failed to get dataset info for session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get dataset info: {str(e)}"
        )

@router.get("/status")
async def get_all_sessions_status():
    """
    Get status of all active sessions.
    
    Returns:
        Dictionary with session statuses
    """
    try:
        sessions = deepeval_session_manager.get_all_sessions()
        
        return {
            "success": True,
            "message": "Session statuses retrieved",
            "sessions": sessions,
            "total_sessions": len(sessions)
        }
        
    except Exception as e:
        logger.error(f"Failed to get session statuses: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session statuses: {str(e)}"
        )

@router.post("/model-api-keys", response_model=SessionModelApiKeysResponse)
async def store_session_model_api_keys(request: SessionModelApiKeysRequest):
    """
    Store or update the model API keys for a session.
    
    Args:
        request: Session model API keys request
        
    Returns:
        Response indicating success/failure
    """
    try:
        deepeval_session_manager.set_session_model_api_keys(
            request.session_id,
            openai_api_key=request.openai_api_key,
            anthropic_api_key=request.anthropic_api_key,
            gemini_api_key=request.gemini_api_key,
            grok_api_key=request.grok_api_key
        )
        
        # Check which keys are now stored (without exposing the actual values)
        stored_keys = deepeval_session_manager.get_session_model_api_keys(request.session_id)
        api_keys_status = {
            provider: key is not None and key.strip() != ""
            for provider, key in stored_keys.items()
        }
        
        return SessionModelApiKeysResponse(
            success=True,
            message="Model API keys stored successfully",
            session_id=request.session_id,
            api_keys=api_keys_status
        )
        
    except Exception as e:
        logger.error(f"Failed to store model API keys for session {request.session_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to store model API keys: {str(e)}"
        )

@router.get("/model-api-keys/{session_id}", response_model=SessionModelApiKeysResponse)
async def get_session_model_api_keys(session_id: str):
    """
    Get the stored model API keys status for a session (without exposing the actual keys).
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        Response with which API keys are available
    """
    try:
        stored_keys = deepeval_session_manager.get_session_model_api_keys(session_id)
        api_keys_status = {
            provider: key is not None and key.strip() != ""
            for provider, key in stored_keys.items()
        }
        
        return SessionModelApiKeysResponse(
            success=True,
            message="Model API keys status retrieved successfully",
            session_id=session_id,
            api_keys=api_keys_status
        )
        
    except Exception as e:
        logger.error(f"Failed to get model API keys for session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get model API keys: {str(e)}"
        ) 