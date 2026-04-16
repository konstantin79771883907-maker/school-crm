"""
API routers package.

Contains FastAPI routers for different API endpoints:
- users: User management
- tickets: Ticket management
- categories: Category management
- comments: Comment management
"""

from app.routers import users, tickets, categories, comments

__all__ = ["users", "tickets", "categories", "comments"]
