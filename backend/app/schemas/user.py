from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import UserRole


# Base User Schema
class UserBase(BaseModel):
    email: EmailStr
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRole = UserRole.USER
    library_id: Optional[str] = None
    is_active: bool = True


# Schema for creating a new user
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    password_confirm: str

    @field_validator('password_confirm')
    def passwords_match(cls, v, info):
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Passwords do not match')
        return v


# Schema for updating a user
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRole] = None
    library_id: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8)
    password_confirm: Optional[str] = None

    @field_validator('password_confirm')
    def passwords_match(cls, v, info):
        if 'password' in info.data and info.data['password'] is not None and v != info.data['password']:
            raise ValueError('Passwords do not match')
        return v


# Schema for user in DB
class UserInDBBase(UserBase):
    id: int
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


# Schema for returning user data
class User(UserInDBBase):
    pass


# Schema for user with additional details
class UserDetail(User):
    library_name: Optional[str] = None


# Schema for user preferences
class UserPreferenceBase(BaseModel):
    theme: str = "light"
    dashboard_layout: Optional[str] = None
    default_library_id: Optional[str] = None
    default_comparison_library_ids: Optional[str] = None
    default_metrics: Optional[str] = None
    email_notifications: bool = True


# Schema for creating user preferences
class UserPreferenceCreate(UserPreferenceBase):
    pass


# Schema for updating user preferences
class UserPreferenceUpdate(BaseModel):
    theme: Optional[str] = None
    dashboard_layout: Optional[str] = None
    default_library_id: Optional[str] = None
    default_comparison_library_ids: Optional[str] = None
    default_metrics: Optional[str] = None
    email_notifications: Optional[bool] = None


# Schema for user preferences in DB
class UserPreferenceInDB(UserPreferenceBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schema for returning user preferences
class UserPreference(UserPreferenceInDB):
    pass


# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user: User


class TokenPayload(BaseModel):
    sub: int  # user_id
    exp: datetime
    role: UserRole


# Password reset schemas
class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordReset(BaseModel):
    token: str
    password: str = Field(..., min_length=8)
    password_confirm: str

    @field_validator('password_confirm')
    def passwords_match(cls, v, info):
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Passwords do not match')
        return v 