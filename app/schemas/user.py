"""
User schemas for request/response validation.

Defines Pydantic models for:
- Creating new users
- Updating existing users
- Returning user data in responses
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema with common attributes."""
    username: str
    email: EmailStr
    role: str = "user"


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user attributes."""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user response data."""
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
