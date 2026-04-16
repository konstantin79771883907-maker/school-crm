"""
Ticket API router.

Provides REST API endpoints for ticket management:
- GET /api/tickets/ - List all tickets
- POST /api/tickets/ - Create new ticket
- GET /api/tickets/{id} - Get ticket by ID
- PUT /api/tickets/{id} - Update ticket
- DELETE /api/tickets/{id} - Delete ticket
"""

from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from app.database import get_session
from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketResponse
from app.routers.users import get_current_user, get_current_user_from_cookie_with_token, require_auth, require_role
from app.models.user import User

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


@router.get("/", response_model=List[TicketResponse])
def get_tickets(
    status_filter: Optional[str] = None,
    priority_filter: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_auth)
):
    """Get all tickets with optional filtering (requires authentication)."""
    query = select(Ticket)
    
    if status_filter:
        query = query.where(Ticket.status == status_filter)
    if priority_filter:
        query = query.where(Ticket.priority == priority_filter)
    
    tickets = session.exec(query.order_by(Ticket.created_at.desc())).all()
    return tickets


@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(
    ticket_data: TicketCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_auth)
):
    """Create a new ticket."""
    ticket = Ticket(
        title=ticket_data.title,
        description=ticket_data.description,
        category_id=ticket_data.category_id,
        user_id=current_user.id,
        updated_at=datetime.utcnow()
    )
    
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: int, 
    session: Session = Depends(get_session),
    current_user: User = Depends(require_auth)
):
    """Get a specific ticket by ID (requires authentication)."""
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    return ticket


@router.put("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_auth)
):
    """Update an existing ticket (requires authentication)."""
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Check permissions: only admin/support can update tickets, or the ticket owner
    if current_user.role not in ["admin", "support"] and ticket.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this ticket"
        )
    
    update_data = ticket_data.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    for key, value in update_data.items():
        setattr(ticket, key, value)
    
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(
    ticket_id: int, 
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["admin", "support"]))
):
    """Delete a ticket (admin/support only)."""
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    session.delete(ticket)
    session.commit()
    return None
