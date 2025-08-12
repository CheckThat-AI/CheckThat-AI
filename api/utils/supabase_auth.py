"""
Supabase Authentication Utilities

Handles Supabase JWT verification and user management.
"""

import os
import jwt
import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests

logger = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_JWT_SECRET = os.getenv('SUPABASE_JWT_SECRET')  # JWT secret from Supabase project settings

# JWT verification
security = HTTPBearer()

class SupabaseAuth:
    def __init__(self):
        if not SUPABASE_URL or not SUPABASE_JWT_SECRET:
            logger.warning("Supabase configuration not found")
        
        # Get JWK Set for JWT verification
        self.jwks_url = f"{SUPABASE_URL}/auth/v1/jwks"
        self.jwks = None
        self._fetch_jwks()
    
    def _fetch_jwks(self):
        """Fetch JSON Web Key Set from Supabase"""
        try:
            if SUPABASE_URL:
                response = requests.get(self.jwks_url)
                if response.status_code == 200:
                    self.jwks = response.json()
                    logger.info("Successfully fetched JWKS from Supabase")
                else:
                    logger.warning(f"Failed to fetch JWKS: {response.status_code}")
        except Exception as e:
            logger.warning(f"Error fetching JWKS: {str(e)}")
    
    def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode Supabase JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload
            
        Raises:
            HTTPException: If token is invalid
        """
        try:
            # First try with the JWT secret
            if SUPABASE_JWT_SECRET:
                payload = jwt.decode(
                    token,
                    SUPABASE_JWT_SECRET,
                    algorithms=["HS256"],
                    audience="authenticated"
                )
                return payload
            
            # If no secret available, try to verify without verification (not recommended for production)
            logger.warning("JWT verification without secret - not recommended for production")
            payload = jwt.decode(token, options={"verify_signature": False})
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
        except Exception as e:
            logger.error(f"Error verifying JWT: {str(e)}")
            raise HTTPException(status_code=401, detail="Authentication failed")

    def extract_user_info(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract user information from JWT payload
        
        Args:
            payload: Decoded JWT payload
            
        Returns:
            Dictionary with user information
        """
        user_metadata = payload.get('user_metadata', {})
        
        return {
            "user_id": payload.get('sub'),
            "email": payload.get('email'),
            "given_name": user_metadata.get('given_name', ''),
            "family_name": user_metadata.get('family_name', ''),
            "picture": user_metadata.get('avatar_url') or user_metadata.get('picture', ''),
            "full_name": user_metadata.get('full_name', ''),
            "provider": user_metadata.get('provider', ''),
            "aud": payload.get('aud'),
            "role": payload.get('role', 'authenticated'),
            "iat": payload.get('iat'),
            "exp": payload.get('exp')
        }

# Initialize Supabase auth instance
supabase_auth = SupabaseAuth()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user from Supabase JWT
    
    Args:
        credentials: HTTP Authorization credentials
        
    Returns:
        User information dictionary
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Extract token from Bearer authorization
        token = credentials.credentials
        
        # Verify and decode token
        payload = supabase_auth.verify_jwt_token(token)
        
        # Extract user information
        user_info = supabase_auth.extract_user_info(payload)
        
        logger.info(f"Authenticated user: {user_info.get('email')}")
        return user_info
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed")

async def get_optional_user(request: Request) -> Optional[Dict[str, Any]]:
    """
    Optional dependency to get current user (doesn't raise exception if not authenticated)
    
    Args:
        request: FastAPI request object
        
    Returns:
        User information dictionary or None if not authenticated
    """
    try:
        # Try to get authorization header
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        # Extract token
        token = auth_header.split(" ")[1]
        
        # Verify and decode token
        payload = supabase_auth.verify_jwt_token(token)
        
        # Extract user information
        user_info = supabase_auth.extract_user_info(payload)
        
        return user_info
        
    except Exception as e:
        logger.debug(f"Optional auth failed: {str(e)}")
        return None

def create_service_response(user_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a standardized response with user information
    
    Args:
        user_info: User information from JWT
        
    Returns:
        Standardized response dictionary
    """
    return {
        "user": {
            "id": user_info.get('user_id'),
            "email": user_info.get('email'),
            "given_name": user_info.get('given_name'),
            "family_name": user_info.get('family_name'),
            "picture": user_info.get('picture'),
            "full_name": user_info.get('full_name')
        },
        "authenticated": True,
        "provider": user_info.get('provider', 'supabase')
    } 