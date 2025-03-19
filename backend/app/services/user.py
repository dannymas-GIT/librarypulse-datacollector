from datetime import datetime, timedelta
import secrets
from typing import Optional, List, Union, Dict, Any

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models.user import User, UserSession, UserPreference
from app.schemas.user import UserCreate, UserUpdate


def get_user(db: Session, user_id: int) -> Optional[User]:
    """
    Get a user by ID.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        User object if found, None otherwise
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Get a user by email.
    
    Args:
        db: Database session
        email: User email
        
    Returns:
        User object if found, None otherwise
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    Get a user by username.
    
    Args:
        db: Database session
        username: Username
        
    Returns:
        User object if found, None otherwise
    """
    return db.query(User).filter(User.username == username).first()


def get_users(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    filters: Optional[Dict[str, Any]] = None
) -> List[User]:
    """
    Get a list of users with optional filtering.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        filters: Optional filters to apply
        
    Returns:
        List of User objects
    """
    query = db.query(User)
    
    if filters:
        if filters.get("email"):
            query = query.filter(User.email.ilike(f"%{filters['email']}%"))
        if filters.get("username"):
            query = query.filter(User.username.ilike(f"%{filters['username']}%"))
        if filters.get("role"):
            query = query.filter(User.role == filters["role"])
        if filters.get("is_active") is not None:
            query = query.filter(User.is_active == filters["is_active"])
        if filters.get("is_verified") is not None:
            query = query.filter(User.is_verified == filters["is_verified"])
    
    return query.offset(skip).limit(limit).all()


def create_user(db: Session, user_in: UserCreate) -> User:
    """
    Create a new user.
    
    Args:
        db: Database session
        user_in: User creation data
        
    Returns:
        Created User object
    """
    db_user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        role=user_in.role,
        library_id=user_in.library_id,
        is_active=user_in.is_active,
        is_verified=False,  # New users are not verified by default
        verification_token=secrets.token_urlsafe(32),
        verification_token_expires=datetime.utcnow() + timedelta(hours=24)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create default preferences
    create_user_preferences(db, db_user.id)
    
    return db_user


def update_user(
    db: Session, 
    user: User, 
    user_in: Union[UserUpdate, Dict[str, Any]]
) -> User:
    """
    Update a user.
    
    Args:
        db: Database session
        user: User object to update
        user_in: User update data
        
    Returns:
        Updated User object
    """
    user_data = user_in if isinstance(user_in, dict) else user_in.dict(exclude_unset=True)
    
    if "password" in user_data and user_data["password"]:
        hashed_password = get_password_hash(user_data["password"])
        del user_data["password"]
        user_data["hashed_password"] = hashed_password
    
    for field, value in user_data.items():
        if hasattr(user, field) and value is not None:
            setattr(user, field, value)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    """
    Delete a user.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        True if the user was deleted, False otherwise
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    
    db.delete(user)
    db.commit()
    return True


def authenticate_user(db: Session, username_or_email: str, password: str) -> Optional[User]:
    """
    Authenticate a user.
    
    Args:
        db: Database session
        username_or_email: Username or email
        password: Password
        
    Returns:
        User object if authentication succeeds, None otherwise
    """
    # Check if input is an email
    if "@" in username_or_email:
        user = get_user_by_email(db, username_or_email)
    else:
        user = get_user_by_username(db, username_or_email)
    
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user


def create_user_session(db: Session, user_id: int, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> UserSession:
    """
    Create a new user session.
    
    Args:
        db: Database session
        user_id: User ID
        ip_address: IP address
        user_agent: User agent
        
    Returns:
        Created UserSession object
    """
    session = UserSession(
        user_id=user_id,
        session_token=secrets.token_urlsafe(32),
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        ip_address=ip_address,
        user_agent=user_agent,
        is_active=True
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def invalidate_user_session(db: Session, session_token: str) -> bool:
    """
    Invalidate a user session.
    
    Args:
        db: Database session
        session_token: Session token
        
    Returns:
        True if the session was invalidated, False otherwise
    """
    session = db.query(UserSession).filter(UserSession.session_token == session_token).first()
    if not session:
        return False
    
    session.is_active = False
    db.add(session)
    db.commit()
    return True


def update_last_login(db: Session, user_id: int) -> Optional[User]:
    """
    Update the last login timestamp for a user.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Updated User object if found, None otherwise
    """
    user = get_user(db, user_id)
    if not user:
        return None
    
    user.last_login = datetime.utcnow()
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_user_preferences(db: Session, user_id: int) -> UserPreference:
    """
    Create default user preferences.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Created UserPreference object
    """
    preferences = UserPreference(
        user_id=user_id,
        theme="light",
        email_notifications=True
    )
    db.add(preferences)
    db.commit()
    db.refresh(preferences)
    return preferences


def get_user_preferences(db: Session, user_id: int) -> Optional[UserPreference]:
    """
    Get user preferences.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        UserPreference object if found, None otherwise
    """
    return db.query(UserPreference).filter(UserPreference.user_id == user_id).first()


def update_user_preferences(
    db: Session, 
    preferences: UserPreference, 
    update_data: Dict[str, Any]
) -> UserPreference:
    """
    Update user preferences.
    
    Args:
        db: Database session
        preferences: UserPreference object to update
        update_data: Update data
        
    Returns:
        Updated UserPreference object
    """
    for field, value in update_data.items():
        if hasattr(preferences, field) and value is not None:
            setattr(preferences, field, value)
    
    db.add(preferences)
    db.commit()
    db.refresh(preferences)
    return preferences


def verify_email(db: Session, verification_token: str) -> Optional[User]:
    """
    Verify a user's email.
    
    Args:
        db: Database session
        verification_token: Verification token
        
    Returns:
        User object if verification succeeds, None otherwise
    """
    user = db.query(User).filter(
        User.verification_token == verification_token,
        User.verification_token_expires > datetime.utcnow()
    ).first()
    
    if not user:
        return None
    
    user.is_verified = True
    user.verification_token = None
    user.verification_token_expires = None
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_password_reset_token(db: Session, email: str) -> Optional[str]:
    """
    Create a password reset token.
    
    Args:
        db: Database session
        email: User email
        
    Returns:
        Password reset token if successful, None otherwise
    """
    user = get_user_by_email(db, email)
    if not user:
        return None
    
    reset_token = secrets.token_urlsafe(32)
    user.password_reset_token = reset_token
    user.password_reset_token_expires = datetime.utcnow() + timedelta(hours=24)
    db.add(user)
    db.commit()
    
    return reset_token


def reset_password(db: Session, reset_token: str, new_password: str) -> Optional[User]:
    """
    Reset a user's password.
    
    Args:
        db: Database session
        reset_token: Password reset token
        new_password: New password
        
    Returns:
        User object if reset succeeds, None otherwise
    """
    user = db.query(User).filter(
        User.password_reset_token == reset_token,
        User.password_reset_token_expires > datetime.utcnow()
    ).first()
    
    if not user:
        return None
    
    user.hashed_password = get_password_hash(new_password)
    user.password_reset_token = None
    user.password_reset_token_expires = None
    db.add(user)
    db.commit()
    db.refresh(user)
    return user 