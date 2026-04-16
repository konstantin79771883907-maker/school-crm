"""
Category schemas for request/response validation.

Defines Pydantic models for:
- Creating new categories
- Updating existing categories
- Returning category data in responses
"""

from pydantic import BaseModel
from typing import Optional


class CategoryBase(BaseModel):
    """Base category schema with common attributes."""
    name: str
    description: str = ""


class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating category attributes."""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    """Schema for category response data."""
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True
