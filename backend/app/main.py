"""
Vizzy FastAPI application factory.

Configures CORS, mounts routers, and provides a health check endpoint.
Also serves the built React frontend as static files when available.
"""
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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


# ─────────────────────────────────────────────
# Serve the built React frontend as static files
# (only if the dist/ folder exists)
# ─────────────────────────────────────────────
_FRONTEND_DIST = Path(__file__).parent.parent.parent / "frontend" / "dist"

if _FRONTEND_DIST.is_dir():
    # Serve static assets (JS, CSS, images)
    app.mount("/assets", StaticFiles(directory=str(_FRONTEND_DIST / "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str) -> FileResponse:
        """Serve the React SPA for all non-API routes (client-side routing support)."""
        index_file = _FRONTEND_DIST / "index.html"
        return FileResponse(str(index_file))
