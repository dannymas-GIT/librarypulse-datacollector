import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

from app.main import app

def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"} 