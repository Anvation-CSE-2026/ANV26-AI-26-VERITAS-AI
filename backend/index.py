"""Vercel ASGI entry point; reuses all existing routes, authentication and middleware."""
import os

from app.config import settings

# Serverless storage cannot safely fall back to an ephemeral/read-only SQLite file.
if os.environ.get("VERCEL") and not settings.database_url.strip():
    raise RuntimeError("DATABASE_URL must be configured for the Vercel backend.")

from app.main import app

__all__ = ["app"]
