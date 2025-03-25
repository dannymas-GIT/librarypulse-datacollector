from fastapi import APIRouter

from app.api.v1.endpoints import auth, datasets, libraries, stats

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(datasets.router)
api_router.include_router(libraries.router)
api_router.include_router(stats.router) 