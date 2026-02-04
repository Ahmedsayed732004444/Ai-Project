"""
FastAPI application for CV parsing.
Integrates with Career_Path .NET database.
"""

import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as cv_router
from app.services.database import test_connection

# ─────────────────────────────────────────────────────────────
# Logging setup
# ─────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)

# ─────────────────────────────────────────────────────────────
# App initialization
# ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="Career Path - CV Parser API",
    description=(
        "AI-powered CV parsing service that integrates with Career_Path database. "
        "Upload CVs and automatically extract structured data into ModelExtration table."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount CV parsing routes
app.include_router(cv_router)


# ─────────────────────────────────────────────────────────────
# Startup and shutdown events
# ─────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    """Test database connection on startup."""
    logger = logging.getLogger(__name__)
    logger.info("Career Path CV Parser API starting up...")
    
    if test_connection():
        logger.info("✓ Database connection verified")
        logger.info("✓ Ready to process CVs")
    else:
        logger.warning("✗ Database connection failed - check credentials")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger = logging.getLogger(__name__)
    logger.info("Shutting down...")


# ─────────────────────────────────────────────────────────────
# Health check endpoints
# ─────────────────────────────────────────────────────────────

@app.get("/health", summary="Health check")
async def health() -> dict[str, str]:
    """API health check."""
    return {"status": "ok", "service": "cv-parser"}


@app.get("/db-health", summary="Database health check")
async def db_health() -> dict[str, str]:
    """Check database connection status."""
    if test_connection():
        return {
            "status": "ok",
            "database": "connected",
            "server": "db38948.public.databaseasp.net"
        }
    else:
        return {
            "status": "error",
            "database": "disconnected"
        }
