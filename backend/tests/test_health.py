import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_health_endpoint(client: TestClient):
    """Test that the health endpoint returns a 200 status code."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["ok", "healthy"] 