"""
app/core/security.py
====================
Password hashing and JWT utilities — the two primitive operations
that every authentication flow in this application is built on top of.
"""

from datetime import datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


# bcrypt is intentionally slow (work factor ~12 rounds by default) which
# makes offline brute-force attacks against stolen hashes computationally expensive
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Converts a plain-text password into a bcrypt hash safe for database storage.
    The hash embeds its own salt so two identical passwords produce different hashes.
    """
    return _pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """
    Returns True when the plain-text password matches the stored bcrypt hash.
    Uses constant-time comparison internally, which prevents timing attacks
    that could reveal whether the password was almost-correct.
    """
    return _pwd_context.verify(password, password_hash)


def create_access_token(subject: Any, expires_delta: timedelta | None = None) -> str:
    """
    Produces a signed JWT containing the user's database ID in the "sub" claim.
    The signature is produced with the application's JWT_SECRET, which means
    any modification to the token after issuing it will fail verification.
    """
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    # "sub" is the standard JWT claim name for the subject (the user being identified)
    payload = {"sub": str(subject), "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decodes the JWT and verifies its signature and expiry in one step.
    python-jose raises JWTError for expired, tampered, or structurally invalid tokens;
    we re-raise as ValueError so callers don't need to import the jose library.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError as exc:
        raise ValueError("Invalid authentication credentials") from exc
