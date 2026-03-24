from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.auth import schemas, service

router = APIRouter(prefix="/auth", tags=["auth"])
bearer_scheme = HTTPBearer()


async def get_current_user_dep(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    user = await service.get_current_user(credentials.credentials, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.post("/signup", response_model=schemas.TokenResponse, status_code=status.HTTP_200_OK)
async def signup(data: schemas.SignupRequest, db: AsyncSession = Depends(get_db)):
    existing = await service.get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    user = await service.create_user(db, data)
    access_token = service.create_access_token(str(user.id))
    return schemas.TokenResponse(
        access_token=access_token,
        user=schemas.UserResponse.model_validate(user),
    )


@router.post("/login", response_model=schemas.TokenResponse)
async def login(data: schemas.LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await service.authenticate_user(db, data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    access_token = service.create_access_token(str(user.id))
    return schemas.TokenResponse(
        access_token=access_token,
        user=schemas.UserResponse.model_validate(user),
    )


@router.post("/logout", response_model=schemas.MessageResponse)
async def logout(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    # Stateless JWT: client discards token. Blocklist is post-MVP.
    return schemas.MessageResponse(message="Logged out successfully")


@router.get("/me", response_model=schemas.UserResponse)
async def get_me(current_user=Depends(get_current_user_dep)):
    return schemas.UserResponse.model_validate(current_user)
