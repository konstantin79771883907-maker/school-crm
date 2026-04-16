"""
Comment schemas for request/response validation.

Defines Pydantic models for:
- Creating new comments
- Returning comment data in responses
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CommentBase(BaseModel):
    """Base comment schema with common attributes."""
    content: str


class CommentCreate(CommentBase):
    """Schema for creating a new comment."""
    ticket_id: int


class CommentResponse(CommentBase):
    """Schema for comment response data."""
    id: int
    ticket_id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
