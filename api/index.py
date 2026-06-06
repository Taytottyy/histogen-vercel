"""Vercel serverless entrypoint — exports the FastAPI ASGI app."""

from app import app

__all__ = ["app"]
