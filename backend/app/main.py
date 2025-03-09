import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger.add("logs/app.log", rotation="10 MB", level="INFO", serialize=False)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    debug=settings.DEBUG
)

# Set up CORS middleware
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Add API routes
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def read_root():
    """Root endpoint that provides basic API information."""
    return {
        "name": settings.PROJECT_NAME,
        "version": "0.1.0",
        "description": "API for the IMLS Library Pulse project",
        "docs_url": "/docs",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    ) 