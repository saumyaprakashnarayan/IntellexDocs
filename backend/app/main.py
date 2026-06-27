"""
app/main.py
===========
Constructs the FastAPI application, wires up middleware, and registers routers.
This is the module Uvicorn imports when the server starts.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.documents import router as documents_router
from app.api.chat import router as chat_router
from app.core.config import settings
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs init_db() once before the server starts accepting requests.
    The yield transfers control to Uvicorn; everything after it runs on shutdown.
    Using a lifespan context manager is the non-deprecated replacement for
    the @app.on_event("startup") pattern that was removed in FastAPI 0.111+.
    """
    await init_db()
    yield


app = FastAPI(
    title="IntellexDocs API",
    description=(
        "RAG backend that lets users upload PDFs and ask Gemini-powered questions "
        "grounded in the document content."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# Browsers enforce the Same-Origin Policy: a page on localhost:3000 is blocked
# from calling localhost:8000 unless the server sends the correct CORS headers.
# This middleware injects those headers on every response.
app.add_middleware(
    CORSMiddleware,
    # str() converts AnyHttpUrl objects (which have a trailing slash) to plain strings
    allow_origins=[str(o) for o in settings.allowed_origins],
    allow_credentials=True,  # required for the Authorization header to be forwarded
    allow_methods=["*"],
    allow_headers=["*"],
)


# Each router owns one domain of the API; the prefix becomes the URL path segment
app.include_router(auth_router,      prefix="/auth",      tags=["Authentication"])
app.include_router(documents_router, prefix="/documents", tags=["Documents"])
app.include_router(chat_router,      prefix="/chat",      tags=["Chat"])
