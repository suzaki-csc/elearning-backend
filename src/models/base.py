"""
Base model for all database models
"""

from sqlalchemy import Column, DateTime, func
from sqlalchemy.ext.declarative import declared_attr
from src.config.database import Base


class BaseModel(Base):
    """Base model with common fields"""
    
    __abstract__ = True
    
    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=func.now(), nullable=False)
    
    @declared_attr
    def updated_at(cls):
        return Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)