from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.auth import (
    Token,
    UserCreate,
    UserResponse,
    PasswordResetRequest,
    PasswordReset,
    EmailVerification,
    UserUpdate
)
from app.services import auth as auth_service

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate
) -> Any:
    """
    Register a new user.
    """
    user = await auth_service.create_user(db, user_in)
    # TODO: Send verification email
    return user

@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = auth_service.authenticate_user(
        db, UserLogin(email=form_data.username, password=form_data.password)
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token = auth_service.create_access_token_for_user(user)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/verify-email", response_model=UserResponse)
def verify_email(
    *,
    db: Session = Depends(get_db),
    verification: EmailVerification
) -> Any:
    """
    Verify user email with token.
    """
    user = auth_service.verify_email(db, verification.token)
    return user

@router.post("/forgot-password")
async def forgot_password(
    *,
    db: Session = Depends(get_db),
    reset_request: PasswordResetRequest
) -> Any:
    """
    Request password reset.
    """
    user = await auth_service.request_password_reset(db, reset_request.email)
    return {"message": "Password reset email sent"}

@router.post("/reset-password", response_model=UserResponse)
def reset_password(
    *,
    db: Session = Depends(get_db),
    reset_data: PasswordReset
) -> Any:
    """
    Reset password with token.
    """
    user = auth_service.reset_password(
        db, reset_data.token, reset_data.new_password
    )
    return user

@router.get("/me", response_model=UserResponse)
def read_users_me(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.put("/me", response_model=UserResponse)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    user_update: UserUpdate
) -> Any:
    """
    Update current user.
    """
    user = auth_service.update_user(db, current_user, user_update)
    return user 