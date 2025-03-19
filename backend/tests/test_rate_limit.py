import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.redis import get_redis

client = TestClient(app)

def test_rate_limit_headers():
    """Test that rate limit headers are present in response."""
    response = client.get("/api/v1/auth/login")
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert "X-RateLimit-Reset" in response.headers

def test_rate_limit_exceeded():
    """Test that rate limit is enforced."""
    # Make requests up to the limit
    for _ in range(5):  # RATE_LIMIT_LOGIN is 5/minute
        response = client.get("/api/v1/auth/login")
        assert response.status_code == 200
    
    # Next request should be rate limited
    response = client.get("/api/v1/auth/login")
    assert response.status_code == 429
    assert response.json() == {"detail": "Too many requests"}

def test_whitelisted_ip():
    """Test that whitelisted IPs are not rate limited."""
    # Set client IP to localhost
    client.headers["X-Forwarded-For"] = "127.0.0.1"
    
    # Make requests beyond the limit
    for _ in range(10):  # More than RATE_LIMIT_LOGIN
        response = client.get("/api/v1/auth/login")
        assert response.status_code == 200

def test_different_endpoints():
    """Test that rate limits are separate for different endpoints."""
    # Make requests to login endpoint
    for _ in range(5):
        response = client.get("/api/v1/auth/login")
        assert response.status_code == 200
    
    # Should still be able to make requests to other endpoints
    response = client.get("/api/v1/auth/register")
    assert response.status_code == 200

@pytest.fixture(autouse=True)
def cleanup_redis():
    """Clean up Redis after each test."""
    redis = get_redis()
    yield
    redis.flushdb() 