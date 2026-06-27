"""
app/api/auth.py
===============
Handles user registration and login.
Registration stores a bcrypt hash of the password, never the plain-text.
Login exchanges credentials for a signed JWT that the client sends on all
subsequent requests via the Authorization: Bearer header.
"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.db.models import User
from app.db.session import get_session
from app.schemas.auth_schemas import Token, UserCreate, UserLogin, UserResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_create: UserCreate,
    session: AsyncSession = Depends(get_session),
) -> UserResponse:
    """
    Creates a new user account if the email address is not already taken.
    Returns 400 rather than 409 for duplicate emails to avoid confirming
    whether a given email is registered to an attacker who is probing accounts.
    """
    existing_user = await session.scalar(
        select(User).filter(User.email == user_create.email)
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    new_user = User(
        name=user_create.name,
        email=user_create.email,
        password_hash=hash_password(user_create.password),
    )
    session.add(new_user)
    await session.commit()
    # refresh() reloads the row from the database so the auto-generated id
    # and server-side created_at timestamp are populated on the object
    await session.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
async def login_user(
    login_data: UserLogin,
    session: AsyncSession = Depends(get_session),
) -> Token:
    """
    Validates credentials and returns a JWT access token on success.
    The same "Incorrect email or password" message is returned whether the
    email doesn't exist or the password is wrong — this prevents enumeration
    attacks that would reveal which emails are registered.
    """
    user = await session.scalar(
        select(User).filter(User.email == login_data.email)
    )

    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    # 24-hour expiry balances security with usability — short enough that a
    # stolen token expires quickly, long enough that users don't re-login constantly
    token = create_access_token(
        subject=user.id,
        expires_delta=timedelta(minutes=60 * 24),
    )
    return Token(access_token=token)
