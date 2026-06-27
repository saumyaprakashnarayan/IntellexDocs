"""
app/db/models.py
================
SQLAlchemy ORM table definitions.
Each class maps one-to-one with a Postgres table.

Relationships:
  User  1──< Document  1──< DocumentChunk
  User  1──< Chat
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """
    Shared metaclass that registers every subclass in SQLAlchemy's metadata
    registry. init_db() calls Base.metadata.create_all() which iterates
    that registry to generate the CREATE TABLE statements.
    """
    pass


class User(Base):
    """
    Represents a registered account. The password_hash field stores a bcrypt
    digest — the plain-text password is never persisted anywhere.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(length=120), nullable=False)

    # unique=True causes Postgres to reject a second INSERT with the same email
    email: Mapped[str] = mapped_column(String(length=240), unique=True, nullable=False)

    # 255 chars gives room for future algorithms that may produce longer hashes
    password_hash: Mapped[str] = mapped_column(String(length=255), nullable=False)

    # server_default calls now() on the database side so the timestamp is set
    # by Postgres, not by the Python process clock
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # cascade="all, delete" propagates the DELETE to related rows automatically,
    # keeping the database consistent without manual cleanup code
    documents = relationship("Document", back_populates="owner", cascade="all, delete")
    chats     = relationship("Chat",     back_populates="user",  cascade="all, delete")


class Document(Base):
    """
    Represents an uploaded PDF. The filename includes a UUID prefix that was
    added during upload to prevent collisions between users with identically-named files.
    """

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # ON DELETE CASCADE means Postgres deletes all Documents when the parent User is deleted
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    filename: Mapped[str] = mapped_column(String(length=255), nullable=False)
    upload_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    pages: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # SHA-256 hex digest of the raw file bytes, used to detect duplicate uploads
    content_hash: Mapped[str] = mapped_column(String(length=255), nullable=True)

    owner  = relationship("User",          back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete")


class DocumentChunk(Base):
    """
    A fixed-size text window extracted from one page of a Document.
    Mirrored in ChromaDB with its embedding vector for semantic search;
    stored here in Postgres so summarisation can fetch chunks by document_id
    without hitting the vector database.
    """

    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    page_number:  Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_index:  Mapped[int] = mapped_column(Integer, nullable=False)
    content:      Mapped[str] = mapped_column(Text, nullable=False)

    # Serialised dict string: {"user_id": "...", "document_id": "...", ...}
    # Stored as text because Postgres JSONB would require an extra dependency
    metadata:     Mapped[str] = mapped_column(Text, nullable=True)

    document = relationship("Document", back_populates="chunks")


class Chat(Base):
    """
    A single question-answer exchange stored for the chat history endpoint.
    Source citations are not persisted here because they are derived at query
    time from ChromaDB and returned directly in the API response.
    """

    __tablename__ = "chats"

    id:         Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id:    Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    question:   Mapped[str] = mapped_column(Text, nullable=False)
    answer:     Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user = relationship("User", back_populates="chats")
