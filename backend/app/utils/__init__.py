# app/utils/__init__.py
# Makes utils a proper Python package so imports like
# `from app.utils.chroma_client import ChromaClient` resolve correctly
# in all environments (editable installs, Docker, pytest, etc.)
