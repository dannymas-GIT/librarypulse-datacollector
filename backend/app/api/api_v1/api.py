from fastapi import APIRouter

from app.api.api_v1.endpoints import datasets, libraries, stats, collector
from app.api.endpoints import library_config, demographics

# Create API router
api_router = APIRouter()

# Include routers for different endpoints
api_router.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
api_router.include_router(libraries.router, prefix="/libraries", tags=["libraries"])
api_router.include_router(stats.router, prefix="/stats", tags=["statistics"])
api_router.include_router(collector.router, prefix="/collector", tags=["data collection"])
api_router.include_router(library_config.router, prefix="/library-config", tags=["library configuration"])
api_router.include_router(demographics.router, prefix="/demographics", tags=["demographics"]) 