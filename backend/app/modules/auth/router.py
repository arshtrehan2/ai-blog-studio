from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta

from ...database import get_db
from ...config import settings
from . import service
from .schemas import UserCreate, UserLogin, TokenResponse, UserResponse
from .models import User

router = APIRouter()
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    user = service.get_current_user_from_token(db, credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Inactive user")
    return user


@router.post("/signup", response_model=TokenResponse, status_code=200)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user and return a JWT access token."""
    existing = service.get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = service.create_user(db, user_data)
    access_token = service.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate and return a JWT access token."""
    user = service.authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = service.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """Client-side logout; server acknowledges. Token blocklist is post-MVP."""
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Return the authenticated user's profile."""
    return current_user
