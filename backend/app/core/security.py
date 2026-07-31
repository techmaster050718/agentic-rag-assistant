from __future__ import annotations

import hashlib
import secrets
import uuid


def generate_session_id() -> str:
    """Generate a cryptographically secure session ID."""
    return str(uuid.uuid4())


def generate_api_key() -> str:
    """Generate a secure API key."""
    return secrets.token_urlsafe(32)


def hash_string(value: str) -> str:
    """SHA-256 hash a string (e.g. for deduplication)."""
    return hashlib.sha256(value.encode()).hexdigest()
