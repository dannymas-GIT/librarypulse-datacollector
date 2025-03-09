from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class TimestampMixin:
    """Mixin that adds created_at and updated_at columns to a model."""
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class IDMixin:
    """Mixin that adds an id column to a model."""
    id = Column(Integer, primary_key=True, index=True) 