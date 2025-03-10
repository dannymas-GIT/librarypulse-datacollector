"""
Main FastAPI application for the Library Pulse API.
"""
import os
import sys
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Add the backend directory to the path so we can import modules
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

# Import API routers
from api.historical_data import router as historical_router
from api.dashboard import router as dashboard_router
from api.libraries import router as libraries_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Library Pulse API",
    description="API for accessing library data and statistics",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Include routers
app.include_router(historical_router)
app.include_router(dashboard_router)
app.include_router(libraries_router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to the Library Pulse API",
        "version": "1.0.0",
        "documentation": "/docs"
    }

# Run the application
if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True) 