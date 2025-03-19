from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, get_current_active_user, get_current_admin_user
from app.models.user import User, UserPreference
from app.schemas.user import (
    User as UserSchema,
    UserCreate,
    UserUpdate,
    UserPreference as UserPreferenceSchema,
    UserPreferenceUpdate
)
from app.services.user import (
    get_user,
    get_users,
    create_user,
    update_user,
    delete_user,
    get_user_by_email,
    get_user_by_username,
    get_user_preferences,
    update_user_preferences
)

router = APIRouter()


@router.get("/me", response_model=UserSchema)
def read_current_user(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.put("/me", response_model=UserSchema)
def update_current_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update current user.
    """
    # Check if email already exists and is not the current user's email
    if user_in.email and user_in.email != current_user.email:
        user = get_user_by_email(db, email=user_in.email)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
    
    # Check if username already exists and is not the current user's username
    if user_in.username and user_in.username != current_user.username:
        user = get_user_by_username(db, username=user_in.username)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )
    
    user = update_user(db, user_id=current_user.id, user_in=user_in)
    return user


@router.get("/preferences", response_model=UserPreferenceSchema)
def read_user_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user preferences.
    """
    preferences = get_user_preferences(db, user_id=current_user.id)
    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User preferences not found",
        )
    return preferences


@router.put("/preferences", response_model=UserPreferenceSchema)
def update_user_preferences_endpoint(
    *,
    db: Session = Depends(get_db),
    preferences_in: UserPreferenceUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update current user preferences.
    """
    preferences = get_user_preferences(db, user_id=current_user.id)
    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User preferences not found",
        )
    
    preferences = update_user_preferences(db, user_id=current_user.id, preferences_in=preferences_in)
    return preferences


# Admin endpoints

@router.get("/", response_model=List[UserSchema])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    email: Optional[str] = Query(None),
    username: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    is_verified: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_admin_user)
) -> Any:
    """
    Retrieve users. Admin only.
    """
    users = get_users(
        db, 
        skip=skip, 
        limit=limit,
        email=email,
        username=username,
        role=role,
        is_active=is_active,
        is_verified=is_verified
    )
    return users


@router.post("/", response_model=UserSchema)
def create_user_endpoint(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Create new user. Admin only.
    """
    # Check if email already exists
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Check if username already exists
    user = db.query(User).filter(User.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    
    user = create_user(db, user_in)
    return user


@router.get("/{user_id}", response_model=UserSchema)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Get a specific user by id. Admin only.
    """
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.put("/{user_id}", response_model=UserSchema)
def update_user_endpoint(
    *,
    user_id: int,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Update a user. Admin only.
    """
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Check if email is being changed and already exists
    if user_in.email and user_in.email != user.email:
        existing_user = db.query(User).filter(User.email == user_in.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
    
    # Check if username is being changed and already exists
    if user_in.username and user_in.username != user.username:
        existing_user = db.query(User).filter(User.username == user_in.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )
    
    user = update_user(db, user, user_in)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
) -> None:
    """
    Delete a user. Admin only.
    """
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Prevent deleting self
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete own user account",
        )
    
    delete_user(db, user_id)
    return None 