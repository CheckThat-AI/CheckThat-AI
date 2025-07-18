"""
Authentication Routes

Handles Supabase authentication verification and user info.
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException

from ..utils.supabase_auth import get_current_user, get_optional_user, create_service_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.get("/me")
async def get_user_info(user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current authenticated user information
    
    Returns:
        User information and authentication status
    """
    try:
        return create_service_response(user)
    except Exception as e:
        logger.error(f"Error getting user info: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user information")

@router.post("/verify")
async def verify_token(user: Dict[str, Any] = Depends(get_current_user)):
    """
    Verify JWT token and return user info
    
    Returns:
        User information if token is valid
    """
    try:
        return {
            "valid": True,
            **create_service_response(user)
        }
    except Exception as e:
        logger.error(f"Error verifying token: {str(e)}")
        raise HTTPException(status_code=500, detail="Token verification failed")

@router.get("/health")
async def auth_health():
    """
    Health check endpoint for authentication service
    
    Returns:
        Service status
    """
    return {
        "status": "healthy",
        "service": "supabase-auth",
        "message": "Authentication service is running"
    } 