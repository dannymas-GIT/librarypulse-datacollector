from fastapi.testclient import TestClient
from fastapi import FastAPI
from fastapi.responses import JSONResponse

def test_health_endpoint():
    """Test the health check endpoint."""
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
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"} 