"""
Vizzy FastAPI application factory.

Configures CORS, mounts routers, and provides a health check endpoint.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .routers import upload, analyze, insights, export

app = FastAPI(
    title="Vizzy API",
    version="1.0.0",
    description="Backend API for the Vizzy data visualization app.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api")
app.include_router(analyze.router, prefix="/api")
app.include_router(insights.router, prefix="/api")
app.include_router(export.router, prefix="/api")


@app.get("/health", tags=["health"])
def health_check() -> dict:
    """Return API health status."""
    return {"status": "ok", "version": "1.0.0"}
