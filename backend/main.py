"""
FastAPI Backend — Main Application Entry Point
AI Interview & Placement Copilot
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import sys

# Configure logging
logger.remove()
logger.add(sys.stdout, format="{time:HH:mm:ss} | {level} | {message}", level="INFO")
logger.add("logs/app.log", rotation="10 MB", retention="7 days", level="DEBUG")

from backend.database.db import init_db
from backend.api.routes import resume, analysis, interview, roadmap, career, analytics


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("🚀 Starting AI Interview & Placement Copilot API...")
    init_db()
    logger.info("✅ Database initialized")
    logger.info("✅ API ready")
    yield
    logger.info("👋 Shutting down API...")


# ── App Creation ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="AI Interview & Placement Copilot",
    description="AI-powered career placement readiness platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── Middleware ─────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global Error Handler ──────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again.", "error": str(exc)},
    )


# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health_check():
    """API health check endpoint."""
    from backend.services.ai_client import get_ai_provider_info
    return {
        "status": "healthy",
        "version": "1.0.0",
        "ai": get_ai_provider_info(),
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "app": "AI Interview & Placement Copilot",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running",
    }


# ── Include Routers ───────────────────────────────────────────────────────────
app.include_router(resume.router, prefix="/api/v1/resume", tags=["Resume"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["Analysis"])
app.include_router(interview.router, prefix="/api/v1/interview", tags=["Interview"])
app.include_router(roadmap.router, prefix="/api/v1/roadmap", tags=["Roadmap"])
app.include_router(career.router, prefix="/api/v1/career", tags=["Career"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=os.getenv("BACKEND_HOST", "127.0.0.1"),
        port=int(os.getenv("BACKEND_PORT", "8000")),
        reload=os.getenv("DEBUG", "True").lower() == "true",
        log_level="info",
    )
