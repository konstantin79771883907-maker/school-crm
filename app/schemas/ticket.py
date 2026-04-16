"""
Ticket schemas for request/response validation.

Defines Pydantic models for:
- Creating new tickets
- Updating existing tickets
- Returning ticket data in responses
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TicketBase(BaseModel):
    """Base ticket schema with common attributes."""
    title: str
    description: str
    priority: str = "medium"
    status: str = "open"
    category_id: Optional[int] = None


class TicketCreate(TicketBase):
    """Schema for creating a new ticket."""
    user_id: Optional[int] = None


class TicketUpdate(BaseModel):
    """Schema for updating ticket attributes."""
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    category_id: Optional[int] = None
    assigned_to_id: Optional[int] = None


class TicketResponse(TicketBase):
    """Schema for ticket response data."""
    id: int
    user_id: int
    assigned_to_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
