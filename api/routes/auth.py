"""
Authentication routes for user management and Google Drive integration
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
import httpx
from supabase import create_client, Client

from ..utils.supabase_auth import get_current_user

logger = logging.getLogger(__name__)

# Initialize Supabase client for admin operations
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY) if SUPABASE_URL and SUPABASE_SERVICE_KEY else None

router = APIRouter(prefix="/auth", tags=["authentication"])

class GoogleTokens(BaseModel):
    accessToken: Optional[str] = None
    refreshToken: Optional[str] = None
    expiresAt: Optional[int] = None

class UserSyncRequest(BaseModel):
    supabaseUserId: str
    email: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    picture: Optional[str] = None
    googleProviderToken: Optional[str] = None
    googleProviderRefreshToken: Optional[str] = None

@router.post("/sync-user")
async def sync_user(
    user_data: UserSyncRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Receives user data and Google tokens from the frontend,
    upserts the user profile, and stores encrypted tokens in the database.
    """
    if current_user.get('user_id') != user_data.supabaseUserId:
        raise HTTPException(status_code=403, detail="User ID mismatch")

    try:
        # Upsert user profile
        user_profile = {
            "id": user_data.supabaseUserId,
            "email": user_data.email,
            "first_name": user_data.firstName,
            "last_name": user_data.lastName,
            "profile_picture": user_data.picture,
        }
        supabase.table("users").upsert(user_profile).execute()

        # Encrypt and store Google tokens
        if user_data.googleProviderToken:
            encryption_key = os.getenv("ENCRYPTION_KEY")
            if not encryption_key:
                raise ValueError("ENCRYPTION_KEY is not set")

            encrypted_access_token = supabase.rpc('pgp_sym_encrypt', {
                'data': user_data.googleProviderToken,
                'p_key': encryption_key
            }).execute().data
            
            encrypted_refresh_token = supabase.rpc('pgp_sym_encrypt', {
                'data': user_data.googleProviderRefreshToken,
                'p_key': encryption_key
            }).execute().data if user_data.googleProviderRefreshToken else None

            token_data = {
                "user_id": user_data.supabaseUserId,
                "encrypted_access_token": encrypted_access_token,
                "encrypted_refresh_token": encrypted_refresh_token,
            }
            supabase.table("user_google_tokens").upsert(token_data).execute()

        return {"status": "success", "message": "User data synced successfully"}
    except Exception as e:
        logger.error(f"Error syncing user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def store_google_tokens(user_id: str, tokens: GoogleTokens):
    """
    Store Google OAuth tokens securely in the database
    """
    try:
        token_record = {
            'user_id': user_id,
            'provider': 'google',
            'access_token': tokens.accessToken,
            'refresh_token': tokens.refreshToken,
            'expires_at': datetime.fromtimestamp(tokens.expiresAt) if tokens.expiresAt else None,
            'scopes': 'drive.file,userinfo.email,userinfo.profile',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
        }

        # Upsert token record (update if exists, insert if new)
        result = supabase.table('user_oauth_tokens').upsert(token_record, on_conflict='user_id,provider').execute()
        
        if result.data:
            logger.info(f"Google tokens stored for user {user_id}")

    except Exception as e:
        logger.error(f"Error storing Google tokens: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to store Google tokens")

@router.get("/google-drive-access/{user_id}")
async def get_google_drive_access(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get valid Google Drive access token for a user
    """
    try:
        # Verify user access
        if current_user.get('user_id') != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Get stored tokens
        result = supabase.table('user_oauth_tokens').select('*').eq('user_id', user_id).eq('provider', 'google').execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="No Google tokens found for user")

        token_data = result.data[0]
        
        # Check if token is still valid
        expires_at = datetime.fromisoformat(token_data['expires_at'].replace('Z', '+00:00'))
        
        if datetime.utcnow() >= expires_at:
            # Token expired, refresh it
            new_token = await refresh_google_token(token_data['refresh_token'])
            if new_token:
                # Update stored token
                await store_google_tokens(user_id, GoogleTokens(
                    accessToken=new_token['access_token'],
                    refreshToken=token_data['refresh_token'],
                    expiresAt=int((datetime.utcnow() + timedelta(seconds=new_token['expires_in'])).timestamp())
                ))
                return {"access_token": new_token['access_token']}
            else:
                raise HTTPException(status_code=401, detail="Failed to refresh Google token")

        return {"access_token": token_data['access_token']}

    except Exception as e:
        logger.error(f"Error getting Google Drive access: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def refresh_google_token(refresh_token: str) -> Optional[Dict[str, Any]]:
    """
    Refresh Google OAuth token
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://oauth2.googleapis.com/token',
                data={
                    'grant_type': 'refresh_token',
                    'refresh_token': refresh_token,
                    'client_id': os.getenv('GOOGLE_CLIENT_ID'),
                    'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to refresh Google token: {response.text}")
                return None

    except Exception as e:
        logger.error(f"Error refreshing Google token: {str(e)}")
        return None

@router.post("/google-drive/upload-file")
async def upload_file_to_drive_and_db(
    file_content: bytes,
    filename: str,
    mime_type: str = "application/octet-stream",
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Upload a file to Google Drive and store reference in Supabase
    """
    try:
        user_id = current_user.get('user_id')
        
        # Get Google Drive access token
        drive_access = await get_google_drive_access(user_id, current_user)
        access_token = drive_access['access_token']

        # Upload to Google Drive
        async with httpx.AsyncClient() as client:
            # Create file metadata
            metadata = {
                'name': filename,
                'parents': ['your-folder-id']  # Optional: specify a folder
            }

            # Upload file
            files = {
                'metadata': (None, str(metadata), 'application/json'),
                'data': (filename, file_content, mime_type)
            }

            response = await client.post(
                'https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart',
                headers={'Authorization': f'Bearer {access_token}'},
                files=files
            )

            if response.status_code == 200:
                drive_file = response.json()
                
                # Store file reference in Supabase
                file_record = {
                    'user_id': user_id,
                    'google_drive_file_id': drive_file['id'],
                    'filename': filename,
                    'mime_type': mime_type,
                    'drive_url': f"https://drive.google.com/file/d/{drive_file['id']}/view",
                    'created_at': datetime.utcnow().isoformat(),
                }

                db_result = supabase.table('user_files').insert(file_record).execute()

                return {
                    "success": True,
                    "google_drive_id": drive_file['id'],
                    "database_id": db_result.data[0]['id'] if db_result.data else None,
                    "drive_url": file_record['drive_url']
                }
            else:
                raise HTTPException(status_code=400, detail=f"Failed to upload to Drive: {response.text}")

    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))