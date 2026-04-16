"""
Comment model definition.

Represents comments on tickets for communication between users and support.
"""

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Comment(SQLModel, table=True):
    """
    Comment model for ticket discussions.
    
    Attributes:
        id: Primary key
        content: Comment text
        created_at: Creation timestamp
        ticket_id: Foreign key to Ticket
        user_id: Foreign key to User (comment author)
    """
    __tablename__ = "comments"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(min_length=1, max_length=5000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Foreign keys
    ticket_id: int = Field(foreign_key="tickets.id")
    user_id: int = Field(foreign_key="users.id")
    
    class Config:
        table = True
