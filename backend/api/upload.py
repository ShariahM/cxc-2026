from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil
from datetime import datetime

router = APIRouter()

# Configure upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/video")
async def upload_video(file: UploadFile = File(...)):
    """
    Upload a video file for analysis.
    
    Args:
        file: Video file to upload
    
    Returns:
        Dict with upload status and file information
    """
    # Validate file type
    if not file.content_type.startswith("video/"):
        raise HTTPException(
            status_code=400,
            detail="File must be a video"
        )
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = Path(file.filename).suffix
    filename = f"{timestamp}_{file.filename}"
    file_path = UPLOAD_DIR / filename
    
    # Save file
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload file: {str(e)}"
        )
    
    return {
        "status": "success",
        "filename": filename,
        "size": file_path.stat().st_size,
        "content_type": file.content_type
    }

@router.get("/list")
async def list_uploads():
    """
    List all uploaded videos.
    
    Returns:
        List of uploaded video files
    """
    files = []
    for file_path in UPLOAD_DIR.glob("*"):
        if file_path.is_file():
            files.append({
                "filename": file_path.name,
                "size": file_path.stat().st_size,
                "created": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat()
            })
    
    return {"files": files}

@router.delete("/{filename}")
async def delete_upload(filename: str):
    """
    Delete an uploaded video file.
    
    Args:
        filename: Name of the file to delete
    
    Returns:
        Deletion status
    """
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )
    
    try:
        file_path.unlink()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete file: {str(e)}"
        )
    
    return {
        "status": "success",
        "message": f"File {filename} deleted"
    }
