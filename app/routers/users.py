"""
User API router.

Provides REST API endpoints for user management:
- GET /api/users/ - List all users
- POST /api/users/ - Create new user
- GET /api/users/{id} - Get user by ID
- PUT /api/users/{id} - Update user
- DELETE /api/users/{id} - Delete user
"""

from fastapi import APIRouter, Depends, HTTPException, status, Form, Request, Response
from sqlmodel import Session, select
from typing import List, Optional
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordRequestForm

from app.database import get_session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserLogin, Token

router = APIRouter(prefix="/api/users", tags=["users"])

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = "your-secret-key-change-in-production"  # Change this in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str, session: Session = Depends(get_session)) -> User:
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_user_from_cookie(request: Request, session: Session = Depends(get_session)) -> Optional[User]:
    """Get current user from cookie."""
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        
        user = session.exec(select(User).where(User.username == username)).first()
        return user
    except (JWTError, Exception):
        return None


async def get_current_user_from_cookie_with_token(session: Session = Depends(get_session), request: Request = None) -> Optional[User]:
    """Get current user from cookie or Authorization header."""
    # Try cookie first
    if request:
        token = request.cookies.get("access_token")
        if token:
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                username: str = payload.get("sub")
                if username:
                    user = session.exec(select(User).where(User.username == username)).first()
                    if user:
                        return user
            except (JWTError, Exception):
                pass
    
    # Try Authorization header
    auth_header = request.headers.get("Authorization") if request else None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username:
                user = session.exec(select(User).where(User.username == username)).first()
                if user:
                    return user
        except (JWTError, Exception):
            pass
    
    return None


def require_auth(current_user: User = Depends(get_current_user_from_cookie_with_token)):
    """Dependency to require authentication."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


def require_role(required_roles: List[str]):
    """Dependency to require specific roles."""
    async def role_checker(current_user: User = Depends(require_auth)):
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {current_user.role} is not authorized. Required: {required_roles}"
            )
        return current_user
    return role_checker


@router.get("/", response_model=List[UserResponse])
def get_users(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_auth)
):
    """Get all users (requires authentication)."""
    users = session.exec(select(User)).all()
    return users


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate, 
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["admin"]))
):
    """Create a new user (admin only)."""
    # Check if username already exists
    existing_user = session.exec(
        select(User).where(User.username == user_data.username)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user with hashed password
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role=user_data.role
    )
    
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int, 
    session: Session = Depends(get_session),
    current_user: User = Depends(require_auth)
):
    """Get a specific user by ID (requires authentication)."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["admin"]))
):
    """Update an existing user (admin only)."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    update_data = user_data.model_dump(exclude_unset=True)
    
    # Hash password if provided
    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))
    
    for key, value in update_data.items():
        setattr(user, key, value)
    
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int, 
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(["admin"]))
):
    """Delete a user (admin only)."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    session.delete(user)
    session.commit()
    return None


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    session: Session = Depends(get_session)
):
    """Login and get access token (OAuth2 compatible)."""
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=UserResponse)
def login_with_cookie(
    form_data: UserLogin,
    session: Session = Depends(get_session),
    response: Response = None
):
    """Login and set cookie (cookie-based auth)."""
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    # Set cookie on response
    if response:
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="lax"
        )
    
    return user
