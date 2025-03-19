from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    datasets,
    libraries,
    stats,
    collector,
    auth,
    users
)

from app.api.endpoints import library_config

# Create API router
api_router = APIRouter()

# Include routers for different endpoints
api_router.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
api_router.include_router(libraries.router, prefix="/libraries", tags=["libraries"])
api_router.include_router(stats.router, prefix="/statistics", tags=["statistics"])
api_router.include_router(collector.router, prefix="/data-collection", tags=["data-collection"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(library_config.router, prefix="/library-config", tags=["library-config"]) 