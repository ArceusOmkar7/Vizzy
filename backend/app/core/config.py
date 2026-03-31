"""Application configuration using Pydantic Settings."""
from typing import Optional, List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    GEMINI_API_KEY: Optional[str] = None
    MAX_UPLOAD_SIZE_MB: int = 50
    SESSION_TTL_MINUTES: int = 30
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    GEMINI_MODEL: str = "gemini-1.5-flash"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
