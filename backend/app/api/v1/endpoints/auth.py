from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db, limiter
from app.core.config import settings
from app.core import security
from app.crud import crud_user
from app.models.user import User
from app.schemas.auth import Token, UserCreate, UserUpdate
from app.schemas.msg import Msg
from app.services import auth as auth_service

router = APIRouter(tags=["auth"])

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = crud_user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            subject=str(user.id), expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/register", response_model=User)
@limiter.limit("3/minute")
async def register(
    request: Request,
    user_in: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Register new user.
    """
    user = crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    user = crud_user.create(db, obj_in=user_in)
    return user

@router.get("/me")
async def get_current_user(
    current_user: User = Depends(crud_user.get_current_user)
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.put("/me")
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(crud_user.get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update current user profile.
    """
    if user_update.current_password:
        if not security.verify_password(user_update.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
    
    user = crud_user.update(db, db_obj=current_user, obj_in=user_update)
    return user

@router.post("/verify-email")
@limiter.limit("3/minute")
async def verify_email(
    request: Request,
    token: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Verify user email.
    """
    user = crud_user.verify_email(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    return user

@router.post("/forgot-password")
@limiter.limit("3/minute")
async def forgot_password(
    request: Request,
    email: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Password recovery email.
    """
    user = crud_user.get_by_email(db, email)
    if user:
        # Create password reset token
        crud_user.create_password_reset_token(user)
        db.commit()
        # Send password reset email (async)
        # await send_reset_password_email(user.email, user.password_reset_token)
    
    return {"detail": "Password reset email sent if email exists"}

@router.post("/reset-password")
@limiter.limit("3/minute")
async def reset_password(
    request: Request,
    token: str,
    new_password: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Reset password.
    """
    user = crud_user.reset_password(db, token, new_password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token"
        )
    return {"detail": "Password reset successful"}

@router.post("/test-token", response_model=User)
def test_token(current_user: User = Depends(crud_user.get_current_user)) -> Any:
    """
    Test access token.
    """
    return current_user 