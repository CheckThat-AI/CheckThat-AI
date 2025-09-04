import os
import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException
from google.oauth2.credentials import Credentials
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaIoBaseDownload
import io
from supabase import create_client, Client
from ..utils.supabase_auth import get_current_user
from fastapi import Depends

logger = logging.getLogger(__name__)

# Supabase client for admin operations
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY) if SUPABASE_URL and SUPABASE_SERVICE_KEY else None

class DriveService:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.credentials = self._get_user_credentials()

    def _get_user_credentials(self) -> Optional[Credentials]:
        """Retrieve and decrypt the user's Google tokens from the database."""
        try:
            encryption_key = os.getenv("ENCRYPTION_KEY")
            if not encryption_key:
                raise ValueError("ENCRYPTION_KEY is not set")

            # Decrypt tokens using Supabase RPC
            tokens_result = supabase.rpc('get_decrypted_google_tokens', {'p_user_id': self.user_id, 'p_key': encryption_key}).execute()
            
            if not tokens_result.data:
                return None

            token_info = tokens_result.data[0]
            return Credentials(
                token=token_info['access_token'],
                refresh_token=token_info.get('refresh_token'),
                token_uri='https://oauth2.googleapis.com/token',
                client_id=os.getenv('GOOGLE_CLIENT_ID'),
                client_secret=os.getenv('GOOGLE_CLIENT_SECRET')
            )
        except Exception as e:
            logger.error(f"Failed to get user credentials: {e}")
            return None

    def download_file_from_drive(self, file_id: str) -> Optional[bytes]:
        """Downloads a file from Google Drive."""
        if not self.credentials:
            raise HTTPException(status_code=401, detail="User is not authenticated with Google")

        try:
            service = build('drive', 'v3', credentials=self.credentials)
            request = service.files().get_media(fileId=file_id)
            file_buffer = io.BytesIO()
            downloader = MediaIoBaseDownload(file_buffer, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
                logger.info(f"Download {int(status.progress() * 100)}%.")
            
            return file_buffer.getvalue()
        except Exception as e:
            logger.error(f"Failed to download file from Drive: {e}")
            return None

    def upload_file_to_supabase_storage(self, file_name: str, file_content: bytes, bucket_name: str = "user-files"):
        """Uploads a file to a user-specific folder in Supabase Storage."""
        try:
            # Path in bucket: /user-files/{user_id}/{file_name}
            storage_path = f"{self.user_id}/{file_name}"
            
            # Use Supabase client to upload
            supabase.storage.from_(bucket_name).upload(
                path=storage_path,
                file=file_content,
                file_options={"content-type": "application/octet-stream", "upsert": "true"}
            )
            
            # Get the public URL
            public_url = supabase.storage.from_(bucket_name).get_public_url(storage_path)
            
            return public_url
        except Exception as e:
            logger.error(f"Failed to upload file to Supabase Storage: {e}")
            raise HTTPException(status_code=500, detail=str(e))

def get_drive_service(current_user: Dict[str, Any] = Depends(get_current_user)) -> DriveService:
    user_id = current_user.get('sub')
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    return DriveService(user_id) 