"""
School Support CRM - Main Application Entry Point

This is the main FastAPI application file that:
- Configures the FastAPI app with CORS, templates, and static files
- Includes all API routers
- Sets up web routes for HTML pages
- Initializes the database with default data
- Provides startup event handlers
"""

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select
from contextlib import asynccontextmanager
import os

from app.database import create_db_and_tables, get_session, engine
from app.models.user import User
from app.models.category import Category
from app.models.ticket import Ticket
from app.routers import users, tickets, categories, comments

# Templates directory setup
templates_directory = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_directory)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


def init_default_data():
    """Initialize database with default users and categories."""
    with Session(engine) as session:
        # Check if default users already exist
        existing_admin = session.exec(
            select(User).where(User.username == "admin")
        ).first()
        
        if not existing_admin:
            # Create default users
            default_users = [
                User(
                    username="admin",
                    email="admin@school.edu",
                    hashed_password=hash_password("admin123"),
                    role="admin"
                ),
                User(
                    username="support",
                    email="support@school.edu",
                    hashed_password=hash_password("support123"),
                    role="support"
                ),
                User(
                    username="user",
                    email="user@school.edu",
                    hashed_password=hash_password("user123"),
                    role="user"
                )
            ]
            
            for user in default_users:
                session.add(user)
            
            # Create default categories
            default_categories = [
                Category(
                    name="Technical Issues",
                    description="Computer, network, and software problems"
                ),
                Category(
                    name="Facilities",
                    description="Building maintenance and facilities requests"
                ),
                Category(
                    name="Academic Support",
                    description="Help with courses, grades, and academic matters"
                )
            ]
            
            for category in default_categories:
                session.add(category)
            
            session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup: Create tables and initialize default data
    create_db_and_tables()
    init_default_data()
    yield
    # Shutdown: cleanup if needed
    pass


# Create FastAPI application
app = FastAPI(
    title="School Support CRM",
    description="Minimalist helpdesk system for school support services",
    version="1.0.0",
    lifespan=lifespan
)

# Include API routers
app.include_router(users.router)
app.include_router(tickets.router)
app.include_router(categories.router)
app.include_router(comments.router)


# Web routes for HTML pages
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, session: Session = Depends(get_session)):
    """Dashboard page with statistics."""
    # Get statistics
    total_tickets = len(session.exec(select(Ticket)).all())
    open_tickets = len(session.exec(
        select(Ticket).where(Ticket.status == "open")
    ).all())
    in_progress_tickets = len(session.exec(
        select(Ticket).where(Ticket.status == "in_progress")
    ).all())
    resolved_tickets = len(session.exec(
        select(Ticket).where(Ticket.status == "resolved")
    ).all())
    
    recent_tickets = session.exec(
        select(Ticket).order_by(Ticket.created_at.desc()).limit(5)
    ).all()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "in_progress_tickets": in_progress_tickets,
        "resolved_tickets": resolved_tickets,
        "recent_tickets": recent_tickets
    })


@app.get("/tickets", response_class=HTMLResponse)
async def tickets_page(request: Request, session: Session = Depends(get_session)):
    """Tickets list page."""
    all_tickets = session.exec(
        select(Ticket).order_by(Ticket.created_at.desc())
    ).all()
    return templates.TemplateResponse("tickets.html", {
        "request": request,
        "tickets": all_tickets
    })


@app.get("/tickets/new", response_class=HTMLResponse)
async def new_ticket_page(request: Request, session: Session = Depends(get_session)):
    """New ticket form page."""
    all_categories = session.exec(select(Category)).all()
    return templates.TemplateResponse("ticket_form.html", {
        "request": request,
        "categories": all_categories,
        "is_edit": False
    })


@app.get("/tickets/{ticket_id}", response_class=HTMLResponse)
async def ticket_detail_page(
    request: Request,
    ticket_id: int,
    session: Session = Depends(get_session)
):
    """Ticket detail page."""
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Get comments for this ticket
    from app.models.comment import Comment
    comments = session.exec(
        select(Comment).where(Comment.ticket_id == ticket_id)
        .order_by(Comment.created_at)
    ).all()
    
    all_categories = session.exec(select(Category)).all()
    
    return templates.TemplateResponse("ticket_detail.html", {
        "request": request,
        "ticket": ticket,
        "comments": comments,
        "categories": all_categories
    })


@app.get("/categories", response_class=HTMLResponse)
async def categories_page(request: Request, session: Session = Depends(get_session)):
    """Categories management page."""
    all_categories = session.exec(select(Category).order_by(Category.name)).all()
    return templates.TemplateResponse("categories.html", {
        "request": request,
        "categories": all_categories
    })
