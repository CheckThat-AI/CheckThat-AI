from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..services.drive_service import DriveService, get_drive_service

router = APIRouter(prefix="/drive", tags=["Google Drive"])

class FileTransferRequest(BaseModel):
    google_drive_file_id: str
    file_name: str

@router.post("/transfer-file-to-supabase")
async def transfer_file(
    request: FileTransferRequest,
    drive_service: DriveService = Depends(get_drive_service)
):
    """
    Downloads a file from Google Drive and uploads it to Supabase Storage.
    """
    # 1. Download from Google Drive
    file_content = drive_service.download_file_from_drive(request.google_drive_file_id)
    if not file_content:
        raise HTTPException(status_code=500, detail="Failed to download file from Google Drive")

    # 2. Upload to Supabase Storage
    supabase_url = drive_service.upload_file_to_supabase_storage(
        file_name=request.file_name,
        file_content=file_content
    )

    return {
        "status": "success",
        "message": "File transferred successfully",
        "supabase_url": supabase_url
    } 