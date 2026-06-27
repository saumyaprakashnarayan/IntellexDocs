"""
app/core/auth.py
================
FastAPI dependency that extracts a JWT from the Authorization header
and resolves it to a live User ORM object.

Any route function that declares `current_user: User = Depends(get_current_user)`
becomes a protected endpoint — unauthenticated requests are rejected before
the route body executes.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.models import User
from app.db.session import get_session


# auto_error=False tells FastAPI not to raise automatically on a missing header;
# we check manually below so we can return a more descriptive error message
_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    """
    Resolves the Bearer JWT in the request header to the authenticated User row.

    Three things are verified in sequence:
      1. A Bearer token is present in the Authorization header.
      2. The token's signature is valid and it has not expired.
      3. The user ID encoded in the token still exists in the database.

    Step 3 catches the case where a user was deleted after their token was issued.
    """
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing.",
        )

    try:
        token_data = decode_access_token(credentials.credentials)
        # "sub" holds the user's database id, stored as a string inside the JWT
        user_id = int(token_data["sub"])
    except (ValueError, KeyError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or has expired.",
        ) from exc

    # Database lookup ensures deleted users are rejected even within a valid token's lifetime
    user = await session.scalar(select(User).filter(User.id == user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found.",
        )

    return user
