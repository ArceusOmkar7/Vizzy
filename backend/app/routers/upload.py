"""Upload router: POST /api/upload, GET /api/session/{id}, DELETE /api/session/{id}"""
from datetime import datetime
from fastapi import APIRouter, UploadFile, File
from ..core.config import settings
from ..core.session import create_session, get_session, delete_session
from ..core.exceptions import FileTooLargeError, InvalidFileTypeError
from ..models.upload import UploadResponse, SessionInfo
from ..utils.file_loader import load_data_from_bytes

router = APIRouter(tags=["upload"])

ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls"}


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)) -> UploadResponse:
    """Upload a CSV or Excel file and create a session."""
    content = await file.read()
    size_bytes = len(content)

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if size_bytes > max_bytes:
        raise FileTooLargeError(size_bytes / (1024 * 1024), settings.MAX_UPLOAD_SIZE_MB)

    filename = file.filename or ""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise InvalidFileTypeError(filename)

    df = load_data_from_bytes(content, filename)
    session_id = create_session(df, filename, size_bytes)
    memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
    null_count = int(df.isnull().sum().sum())

    return UploadResponse(
        session_id=session_id,
        filename=filename,
        rows=len(df),
        columns=len(df.columns),
        size_bytes=size_bytes,
        memory_mb=round(memory_mb, 3),
        null_count=null_count,
        upload_time=datetime.utcnow(),
    )


@router.get("/session/{session_id}", response_model=SessionInfo)
def get_session_info(session_id: str) -> SessionInfo:
    """Get basic information about an existing session."""
    session = get_session(session_id)
    df = session["df"]
    memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
    null_count = int(df.isnull().sum().sum())
    return SessionInfo(
        session_id=session_id,
        filename=session["filename"],
        rows=len(df),
        columns=len(df.columns),
        size_bytes=session["size_bytes"],
        memory_mb=round(memory_mb, 3),
        null_count=null_count,
        uploaded_at=session["uploaded_at"],
        last_accessed=session["last_accessed"],
    )


@router.delete("/session/{session_id}")
def remove_session(session_id: str) -> dict:
    """Delete a session and free its memory."""
    delete_session(session_id)
    return {"status": "deleted", "session_id": session_id}
