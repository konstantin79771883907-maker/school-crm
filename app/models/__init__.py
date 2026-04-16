"""
Database models package.

Contains all SQLModel models for the CRM system:
- User: System users with roles
- Ticket: Support tickets
- Category: Ticket categories
- Comment: Ticket comments
"""

from app.models.user import User
from app.models.ticket import Ticket
from app.models.category import Category
from app.models.comment import Comment

__all__ = ["User", "Ticket", "Category", "Comment"]
