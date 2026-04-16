"""
Ticket model definition.

Represents support tickets with priorities, statuses, and relationships
to users and categories.
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime


class Ticket(SQLModel, table=True):
    """
    Support ticket model.
    
    Attributes:
        id: Primary key
        title: Short descriptive title
        description: Detailed problem description
        status: Current status (open/in_progress/resolved/closed)
        priority: Priority level (low/medium/high)
        created_at: Creation timestamp
        updated_at: Last update timestamp
        user_id: Foreign key to User (ticket creator)
        category_id: Foreign key to Category
        assigned_to_id: Foreign key to User (support staff assigned)
    """
    __tablename__ = "tickets"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(min_length=1, max_length=200, index=True)
    description: str = Field(min_length=1, max_length=5000)
    status: str = Field(default="open", description="open, in_progress, resolved, closed")
    priority: str = Field(default="medium", description="low, medium, high")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Foreign keys
    user_id: int = Field(foreign_key="users.id")
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    assigned_to_id: Optional[int] = Field(default=None, foreign_key="users.id")
    
    # Relationships
    # Note: Relationships are defined here but imported in __init__.py
    
    class Config:
        table = True
