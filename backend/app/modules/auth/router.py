from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.database import get_db
from .schemas import SignupRequest, LoginRequest, TokenResponse, MessageResponse, UserOut
from .service import signup, login, get_current_user
from .models import User

router = APIRouter()


@router.post("/signup", response_model=TokenResponse, status_code=201)
def signup_endpoint(payload: SignupRequest, db: Session = Depends(get_db)):
    user, token = signup(db, payload)
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=TokenResponse)
def login_endpoint(payload: LoginRequest, db: Session = Depends(get_db)):
    user, token = login(db, payload)
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.post("/logout", response_model=MessageResponse)
def logout_endpoint(
    response: Response,
    current_user: User = Depends(get_current_user),
):
    # Client-side token discard; httpOnly cookie cleared here for completeness
    response.delete_cookie("refresh_token")
    return MessageResponse(message="Logged out successfully")


@router.get("/me", response_model=UserOut)
def me_endpoint(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)
