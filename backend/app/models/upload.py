"""Pydantic models for file upload responses."""
from pydantic import BaseModel
from datetime import datetime


class UploadResponse(BaseModel):
    """Response model for successful file upload."""
    session_id: str
    filename: str
    rows: int
    columns: int
    size_bytes: int
    memory_mb: float
    null_count: int
    upload_time: datetime


class SessionInfo(BaseModel):
    """Basic session information."""
    session_id: str
    filename: str
    rows: int
    columns: int
    size_bytes: int
    memory_mb: float
    null_count: int
    uploaded_at: datetime
    last_accessed: datetime
