from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VideoMetadata(BaseModel):
    """Model for video metadata"""
    filename: str
    size: int
    upload_date: datetime
    duration: Optional[float] = None
    resolution: Optional[str] = None
    format: Optional[str] = None

class VideoAnalysis(BaseModel):
    """Model for video analysis results"""
    video_id: str
    analysis_type: str
    timestamp: datetime
    results: dict
    confidence: Optional[float] = None
