import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from jose import jwt

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin
from app.services import auth as auth_service
from app.schemas.user import Token

@pytest.fixture
async def test_user(db: Session):
    """Create a test user."""
    user_in = UserCreate(
        email="test@example.com",
        username="testuser",
        password="testpassword123",
        first_name="Test",
        last_name="User"
    )
    user = await auth_service.create_user(db, user_in)
    return user

@pytest.fixture
def test_user_token(test_user: User):
    """Create a test user token."""
    return create_access_token(test_user.id)

def test_login_success(client: TestClient, test_user: User):
    """Test successful login."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Verify token
    token = data["access_token"]
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == str(test_user.id)

def test_login_invalid_credentials(client: TestClient, test_user: User):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect email or password"}

def test_login_nonexistent_user(client: TestClient):
    """Test login with non-existent user."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect email or password"}

def test_login_inactive_user(client: TestClient, db: Session, test_user: User):
    """Test login with inactive user."""
    # Deactivate user
    test_user.is_active = False
    db.commit()
    
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Inactive user"}

def test_login_rate_limit(client: TestClient, test_user: User):
    """Test login rate limiting."""
    # Make requests up to the limit
    for _ in range(5):  # RATE_LIMIT_LOGIN is 5/minute
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
    
    # Next request should be rate limited
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 429
    assert response.json() == {"detail": "Too many requests"}

def test_get_current_user(client: TestClient, test_user: User, test_user_token: str):
    """Test getting current user."""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["username"] == test_user.username
    assert data["first_name"] == test_user.first_name
    assert data["last_name"] == test_user.last_name

def test_get_current_user_invalid_token(client: TestClient):
    """Test getting current user with invalid token."""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}

def test_get_current_user_expired_token(client: TestClient, test_user: User):
    """Test getting current user with expired token."""
    # Create expired token
    expired_token = create_access_token(
        test_user.id,
        expires_delta=timedelta(minutes=-1)
    )
    
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}

def test_get_current_user_no_token(client: TestClient):
    """Test getting current user without token."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

def test_update_user_profile(client: TestClient, test_user: User, test_user_token: str):
    """Test updating user profile."""
    response = client.put(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={
            "first_name": "Updated",
            "last_name": "Name",
            "current_password": "testpassword123",
            "new_password": "newpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Updated"
    assert data["last_name"] == "Name"
    
    # Verify password was updated
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "newpassword123"
        }
    )
    assert response.status_code == 200

def test_update_user_profile_wrong_password(client: TestClient, test_user: User, test_user_token: str):
    """Test updating user profile with wrong current password."""
    response = client.put(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={
            "first_name": "Updated",
            "last_name": "Name",
            "current_password": "wrongpassword",
            "new_password": "newpassword123"
        }
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Current password is incorrect"}

@pytest.fixture(autouse=True)
def cleanup_redis():
    """Clean up Redis after each test."""
    from app.core.redis import get_redis
    redis = get_redis()
    yield
    redis.flushdb()

def test_register(client: TestClient, db: Session):
    """Test user registration."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "Test123!@#",
        "first_name": "Test",
        "last_name": "User"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    
    # Check response data
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert data["first_name"] == user_data["first_name"]
    assert data["last_name"] == user_data["last_name"]
    assert "id" in data
    assert "is_active" in data
    assert "is_verified" in data
    assert "verification_token" in data
    
    # Check database
    user = db.query(User).filter(User.email == user_data["email"]).first()
    assert user is not None
    assert user.email == user_data["email"]
    assert user.username == user_data["username"]
    assert user.is_active is True
    assert user.is_verified is False
    assert user.verification_token is not None

def test_login(client: TestClient, db: Session):
    """Test user login."""
    # Create a verified user
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="Test123!@#",
        first_name="Test",
        last_name="User"
    )
    user = User(
        email=user_data.email,
        username=user_data.username,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        hashed_password=auth_service.get_password_hash(user_data.password),
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Test login
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": user_data.email,
            "password": user_data.password
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_verify_email(client: TestClient, db: Session):
    """Test email verification."""
    # Create an unverified user
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="Test123!@#",
        first_name="Test",
        last_name="User"
    )
    user = User.from_schema(user_data)
    db.add(user)
    db.commit()
    
    # Test verification
    response = client.post("/api/v1/auth/verify-email", json={"token": user.verification_token})
    assert response.status_code == 200
    data = response.json()
    
    # Check response data
    assert data["email"] == user_data.email
    assert data["is_verified"] is True
    
    # Check database
    user = db.query(User).filter(User.email == user_data.email).first()
    assert user.is_verified is True

def test_forgot_password(client: TestClient, db: Session):
    """Test password reset request."""
    # Create a verified user
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="Test123!@#",
        first_name="Test",
        last_name="User"
    )
    user = User.from_schema(user_data)
    user.is_verified = True
    db.add(user)
    db.commit()
    
    # Test password reset request
    response = client.post("/api/v1/auth/forgot-password", json={"email": user_data.email})
    assert response.status_code == 200
    data = response.json()
    
    # Check response data
    assert data["detail"] == "Password reset email sent if email exists"
    
    # Check database
    user = db.query(User).filter(User.email == user_data.email).first()
    assert user.password_reset_token is not None
    assert user.password_reset_token_expires is not None

def test_reset_password(client: TestClient, db: Session):
    """Test password reset."""
    # Create a verified user with reset token
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="Test123!@#",
        first_name="Test",
        last_name="User"
    )
    user = User.from_schema(user_data)
    user.is_verified = True
    user.create_password_reset_token()
    db.add(user)
    db.commit()
    
    # Test password reset
    reset_data = {
        "token": user.password_reset_token,
        "new_password": "NewTest123!@#"
    }
    response = client.post("/api/v1/auth/reset-password", json=reset_data)
    assert response.status_code == 200
    data = response.json()
    
    # Check response data
    assert data["detail"] == "Password reset successful"
    
    # Check database
    user = db.query(User).filter(User.email == user_data.email).first()
    assert user.password_reset_token is None
    assert user.password_reset_token_expires is None
    
    # Try login with new password
    login_data = {
        "username": "testuser",
        "password": "NewTest123!@#"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200 