"""
User model definition.

Represents system users with different roles:
- user: Regular user who can create tickets
- support: Support staff who can manage tickets
- admin: Administrator with full access
"""

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class User(SQLModel, table=True):
    """
    User model for authentication and authorization.
    
    Attributes:
        id: Primary key
        username: Unique username for login
        email: User email address
        hashed_password: Bcrypt hashed password
        role: User role (user/support/admin)
        is_active: Whether the account is active
        created_at: Account creation timestamp
    """
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, min_length=3, max_length=50)
    email: str = Field(unique=True, index=True)
    hashed_password: str = Field(min_length=60)
    role: str = Field(default="user", description="user, support, or admin")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        table = True
