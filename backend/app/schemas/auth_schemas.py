"""
app/schemas/auth_schemas.py
============================
Pydantic models (schemas) for the authentication API.

These classes define:
  - What JSON the API accepts as input (request bodies)
  - What JSON the API sends back as output (response bodies)

Pydantic validates incoming data automatically and raises a 422 Unprocessable
Entity response if the data doesn't match the schema — no manual validation code needed.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Payload for POST /auth/register."""

    name: str       # Display name, e.g. "Alice Smith"
    email: EmailStr # Pydantic validates that this is a valid email format
    password: str   # Plain text — will be hashed before storage


class UserLogin(BaseModel):
    """Payload for POST /auth/login."""

    email: EmailStr
    password: str


class Token(BaseModel):
    """Response from POST /auth/login — contains the JWT access token."""

    access_token: str
    token_type: str = "bearer"  # Always "bearer" per the OAuth2 spec


class UserResponse(BaseModel):
    """
    Public user representation returned after registration.

    Excludes the password_hash — never expose hashed passwords in responses.
    """

    id: int
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        # Allow Pydantic to read data from SQLAlchemy ORM objects,
        # not just plain dicts.  Required for `from_orm()` to work.
        from_attributes = True  # Pydantic v2 name (was orm_mode in v1)
