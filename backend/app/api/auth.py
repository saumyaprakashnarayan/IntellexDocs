from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import create_access_token, hash_password, verify_password
from app.db.models import User
from app.db.session import get_session
from app.schemas.auth_schemas import Token, UserCreate, UserLogin, UserResponse

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register_user(user_create: UserCreate, session: AsyncSession = Depends(get_session)) -> UserResponse:
    existing = await session.scalar(select(User).filter(User.email == user_create.email))
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = User(
        name=user_create.name,
        email=user_create.email,
        password_hash=hash_password(user_create.password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@router.post("/login", response_model=Token)
async def login_user(login_data: UserLogin, session: AsyncSession = Depends(get_session)) -> Token:
    user = await session.scalar(select(User).filter(User.email == login_data.email))
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(subject=user.id, expires_delta=timedelta(minutes=60))
    return Token(access_token=token)
