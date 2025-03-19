from datetime import timedelta
from typing import Any, Dict

from fastapi import APIRouter, Body, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_db, get_current_user
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.user import Token, UserCreate, User as UserSchema, PasswordResetRequest, PasswordReset
from app.services.user import (
    authenticate_user, create_user, get_user_by_email, get_user_by_username,
    create_user_session, invalidate_user_session, verify_email,
    create_password_reset_token, reset_password, update_last_login
)
from app.utils.email import send_verification_email, send_password_reset_email

router = APIRouter()


@router.post("/register", response_model=UserSchema)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    Register a new user.
    """
    # Check if user exists
    user = get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists",
        )
    
    # Check if username exists
    user = get_user_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this username already exists",
        )
    
    # Create user
    user = create_user(db, user_in)
    
    # Send verification email
    if settings.EMAILS_ENABLED:
        send_verification_email(
            email_to=user.email,
            user_id=user.id,
            username=user.username
        )
    
    return user


@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    # Create session
    ip_address = request.client.host if request else None
    user_agent = request.headers.get("User-Agent") if request else None
    session = create_user_session(db, user.id, ip_address, user_agent)
    
    # Update last login time
    user.last_login = session.created_at
    db.add(user)
    db.commit()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_at": session.expires_at,
        "user": user,
    }


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    session_token: str = Body(...),
) -> Any:
    """
    Logout and invalidate session.
    """
    success = invalidate_user_session(db, session_token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session token",
        )
    
    return {"detail": "Successfully logged out"}


@router.post("/verify-email", response_model=UserSchema)
def verify_email_endpoint(
    *,
    db: Session = Depends(get_db),
    token: str = Body(...),
) -> Any:
    """
    Verify email address.
    """
    user = verify_email(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )
    
    return user


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(
    *,
    db: Session = Depends(get_db),
    email_in: PasswordResetRequest,
) -> Any:
    """
    Request password reset.
    """
    user = get_user_by_email(db, email=email_in.email)
    if not user:
        # Don't reveal that the email doesn't exist
        return {"detail": "Password reset email sent if email exists"}
    
    reset_token = create_password_reset_token(db, email_in.email)
    
    # Send password reset email
    if settings.EMAILS_ENABLED:
        send_password_reset_email(
            email_to=user.email,
            username=user.username,
            reset_token=reset_token
        )
    
    return {"detail": "Password reset email sent if email exists"}


@router.post("/reset-password", response_model=UserSchema)
def reset_password_endpoint(
    *,
    db: Session = Depends(get_db),
    reset_data: PasswordReset,
) -> Any:
    """
    Reset password.
    """
    user = reset_password(db, reset_data.token, reset_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )
    
    return user 