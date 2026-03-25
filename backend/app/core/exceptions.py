"""Custom HTTP exceptions for the Vizzy API."""
from fastapi import HTTPException, status


class SessionNotFoundError(HTTPException):
    def __init__(self, session_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found or expired.",
        )


class FileTooLargeError(HTTPException):
    def __init__(self, size_mb: float, max_mb: int):
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size {size_mb:.1f} MB exceeds maximum allowed {max_mb} MB.",
        )


class InvalidFileTypeError(HTTPException):
    def __init__(self, filename: str):
        super().__init__(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File '{filename}' has an unsupported type. Allowed: csv, xlsx, xls.",
        )
