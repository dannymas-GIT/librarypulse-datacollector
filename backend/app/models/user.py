from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table, DateTime, Text, Enum, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime
from typing import Optional

from app.db.base import Base, IDMixin, TimestampMixin


class UserRole(str, enum.Enum):
    """Enum for user roles"""
    ADMIN = "admin"
    LIBRARIAN = "librarian"
    ANALYST = "analyst"
    USER = "user"


class User(Base, IDMixin, TimestampMixin):
    """Model representing a user in the system."""
    
    __tablename__ = "users"
    
    # User identity
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    
    # Authentication
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String(255), nullable=True)
    verification_token_expires = Column(DateTime(timezone=True), nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_token_expires = Column(DateTime(timezone=True), nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # User information
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    
    # Library association (optional - for librarians)
    library_id = Column(String(20), nullable=True)
    dataset_id = Column(Integer, nullable=True)
    __table_args__ = (
        ForeignKeyConstraint(['dataset_id', 'library_id'], ['libraries.dataset_id', 'libraries.library_id']),
    )
    
    # Relationships
    library = relationship("Library", back_populates="users")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.username}>"


class UserSession(Base, IDMixin, TimestampMixin):
    """Model representing a user session."""
    
    __tablename__ = "user_sessions"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self):
        return f"<UserSession {self.session_token[:8]}...>"


class UserPreference(Base, IDMixin, TimestampMixin):
    """Model representing user preferences."""
    
    __tablename__ = "user_preferences"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, unique=True)
    
    # UI preferences
    theme = Column(String(20), default="light", nullable=False)
    dashboard_layout = Column(Text, nullable=True)  # JSON string of dashboard layout
    
    # Default settings
    default_library_id = Column(String(20), nullable=True)
    default_dataset_id = Column(Integer, nullable=True)
    __table_args__ = (
        ForeignKeyConstraint(['default_dataset_id', 'default_library_id'], ['libraries.dataset_id', 'libraries.library_id']),
    )
    default_comparison_library_ids = Column(Text, nullable=True)  # Comma-separated list of library IDs
    default_metrics = Column(Text, nullable=True)  # Comma-separated list of metrics
    
    # Email preferences
    email_notifications = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="preferences")
    default_library = relationship("Library", foreign_keys=[default_dataset_id, default_library_id])
    
    def __repr__(self):
        return f"<UserPreference for user_id={self.user_id}>"


# Add the relationship to the Library model
# This will be imported in __init__.py to avoid circular imports 