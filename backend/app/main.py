import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.core.rate_limit import setup_rate_limiting

# Configure logging
logging.basicConfig(level=logging.INFO)
logger.add("logs/app.log", rotation="10 MB", level="INFO", serialize=False)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Library Pulse API",
    description="API for collecting and analyzing public library data",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up rate limiting
setup_rate_limiting(app)

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/health", status_code=200)
def health_check():
    return "OK"

@app.get("/api/health", status_code=200)
def api_health_check():
    return JSONResponse(content={"status": "healthy"})

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

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    ) 