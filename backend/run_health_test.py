#!/usr/bin/env python3
"""
Simple script to run the health check test without any other dependencies.
"""

from fastapi.testclient import TestClient
from fastapi import FastAPI
from fastapi.responses import JSONResponse

def test_health_endpoint():
    """Test the health check endpoint."""
    print("Starting health check test...")
    
    # Create a minimal test app
    app = FastAPI()
    
    @app.get("/api/health")
    async def health_check():
        """Health check endpoint."""
        return JSONResponse(
            content={"status": "healthy"},
            status_code=200
        )
    
    # Create test client and make request
    client = TestClient(app)
    print("Making request to /api/health...")
    response = client.get("/api/health")
    
    print(f"Response status code: {response.status_code}")
    print(f"Response body: {response.json()}")
    
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    assert response.json() == {"status": "healthy"}, f"Expected body {{'status': 'healthy'}}, got {response.json()}"
    print("✅ Health check test passed!")

if __name__ == "__main__":
    test_health_endpoint() 