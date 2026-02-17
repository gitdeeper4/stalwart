"""STALWART API server."""

from typing import Optional
import uvicorn
from fastapi import FastAPI

from ..utils.logger import get_logger

logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="STALWART API",
    description="Bridge Health Monitoring System API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "STALWART API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


def start_api(host: str = "0.0.0.0", port: int = 8000, debug: bool = False):
    """Start the API server."""
    logger.info(f"Starting API server on {host}:{port}")
    uvicorn.run(
        "src.stalwart.api.app:app",
        host=host,
        port=port,
        reload=debug,
        log_level="debug" if debug else "info"
    )
