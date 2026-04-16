"""
Comment API router.

Provides REST API endpoints for comment management:
- GET /api/comments/ - List all comments (optionally by ticket)
- POST /api/comments/ - Create new comment
- GET /api/comments/{id} - Get comment by ID
- DELETE /api/comments/{id} - Delete comment
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List, Optional

from app.database import get_session
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentResponse

router = APIRouter(prefix="/api/comments", tags=["comments"])


@router.get("/", response_model=List[CommentResponse])
def get_comments(
    ticket_id: Optional[int] = Query(None),
    session: Session = Depends(get_session)
):
    """Get all comments, optionally filtered by ticket ID."""
    query = select(Comment).order_by(Comment.created_at)
    
    if ticket_id:
        query = query.where(Comment.ticket_id == ticket_id)
    
    comments = session.exec(query).all()
    return comments


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(comment_data: CommentCreate, session: Session = Depends(get_session)):
    """Create a new comment on a ticket."""
    comment = Comment.model_validate(comment_data)
    
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment


@router.get("/{comment_id}", response_model=CommentResponse)
def get_comment(comment_id: int, session: Session = Depends(get_session)):
    """Get a specific comment by ID."""
    comment = session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    return comment


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: int, session: Session = Depends(get_session)):
    """Delete a comment."""
    comment = session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    session.delete(comment)
    session.commit()
    return None
