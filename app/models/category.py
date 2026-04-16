"""
Category model definition.

Represents ticket categories for organizing support requests.
"""

from sqlmodel import SQLModel, Field
from typing import Optional


class Category(SQLModel, table=True):
    """
    Category model for ticket classification.
    
    Attributes:
        id: Primary key
        name: Category name (unique)
        description: Category description
        is_active: Whether category is available for selection
    """
    __tablename__ = "categories"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    is_active: bool = Field(default=True)
    
    class Config:
        table = True
