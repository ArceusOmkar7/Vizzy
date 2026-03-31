"""Thread-safe in-memory session store with TTL cleanup."""
import uuid
import threading
from datetime import datetime, timedelta
from typing import Dict, Any
import pandas as pd
from .config import settings
from .exceptions import SessionNotFoundError


sessions: Dict[str, Dict[str, Any]] = {}
_lock = threading.Lock()


def create_session(df: pd.DataFrame, filename: str, size_bytes: int) -> str:
    """Create a new session and return the session_id (UUID)."""
    session_id = str(uuid.uuid4())
    with _lock:
        sessions[session_id] = {
            "df": df,
            "filename": filename,
            "size_bytes": size_bytes,
            "uploaded_at": datetime.utcnow(),
            "last_accessed": datetime.utcnow(),
        }
    return session_id


def get_session(session_id: str) -> Dict[str, Any]:
    """Get session by ID, updating last_accessed. Raises SessionNotFoundError if missing."""
    with _lock:
        session = sessions.get(session_id)
        if session is None:
            raise SessionNotFoundError(session_id)
        session["last_accessed"] = datetime.utcnow()
        return session


def delete_session(session_id: str) -> None:
    """Delete a session by ID."""
    with _lock:
        sessions.pop(session_id, None)


def cleanup_expired_sessions() -> int:
    """Remove sessions older than SESSION_TTL_MINUTES. Returns count removed."""
    cutoff = datetime.utcnow() - timedelta(minutes=settings.SESSION_TTL_MINUTES)
    removed = 0
    with _lock:
        expired = [sid for sid, s in sessions.items() if s["last_accessed"] < cutoff]
        for sid in expired:
            del sessions[sid]
            removed += 1
    return removed
