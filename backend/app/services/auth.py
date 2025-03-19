from datetime import datetime, timedelta
from typing import Optional
import secrets
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin, PasswordResetRequest, UserUpdate
from app.services.email import send_verification_email, send_password_reset_email

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

async def create_user(db: Session, user_in: UserCreate) -> User:
    # Check if user with email exists
    if get_user_by_email(db, user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username is taken
    if get_user_by_username(db, user_in.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create verification token
    verification_token = secrets.token_urlsafe(32)
    
    # Create new user
    db_user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        verification_token=verification_token
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Send verification email
    await send_verification_email(
        email_to=user_in.email,
        username=user_in.username,
        verification_token=verification_token
    )
    
    return db_user

def authenticate_user(db: Session, user_in: UserLogin) -> Optional[User]:
    user = get_user_by_email(db, user_in.email)
    if not user:
        return None
    if not verify_password(user_in.password, user.hashed_password):
        return None
    return user

def create_access_token_for_user(user: User) -> str:
    access_token_expires = timedelta(minutes=60 * 24 * 7)  # 7 days
    return create_access_token(
        subject=user.id,
        expires_delta=access_token_expires
    )

def verify_email(db: Session, token: str) -> User:
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    
    user.is_verified = True
    user.verification_token = None
    db.commit()
    db.refresh(user)
    return user

async def request_password_reset(db: Session, email: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        # Don't reveal if email exists
        return None
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    user.reset_password_token = reset_token
    user.reset_password_expires = datetime.utcnow() + timedelta(hours=24)
    
    db.commit()
    db.refresh(user)
    
    # Send password reset email
    await send_password_reset_email(
        email_to=user.email,
        username=user.username,
        reset_token=reset_token
    )
    
    return user

def reset_password(db: Session, token: str, new_password: str) -> User:
    user = db.query(User).filter(
        User.reset_password_token == token,
        User.reset_password_expires > datetime.utcnow()
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    user.hashed_password = get_password_hash(new_password)
    user.reset_password_token = None
    user.reset_password_expires = None
    
    db.commit()
    db.refresh(user)
    return user

def update_user(db: Session, user: User, user_update: UserUpdate) -> User:
    if user_update.current_password and user_update.new_password:
        if not verify_password(user_update.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        user.hashed_password = get_password_hash(user_update.new_password)
    
    if user_update.first_name is not None:
        user.first_name = user_update.first_name
    if user_update.last_name is not None:
        user.last_name = user_update.last_name
    
    db.commit()
    db.refresh(user)
    return user 