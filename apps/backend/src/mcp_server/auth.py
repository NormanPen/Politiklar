"""Authentication and API token verification for Politiklar MCP Server."""

from datetime import datetime, timezone
import hashlib
import os

from mcp.server.mcpserver.exceptions import ToolError
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.relational.models import UserApiKey


def verify_mcp_token(session: Session, token: str | None = None) -> bool:
    """Verifies that the provided API key token is valid and active in the database."""
    # Read from parameter or environment variable
    raw_token = token or os.environ.get("POLITIKLAR_API_KEY")
    if not raw_token:
        # If authentication is explicitly disabled (e.g. in local dev testing without keys)
        allow_anonymous = os.environ.get("POLITIKLAR_ALLOW_ANONYMOUS_MCP", "false").lower() in ("true", "1")
        return allow_anonymous

    clean_token = raw_token.strip()
    key_hash = hashlib.sha256(clean_token.encode("utf-8")).hexdigest()

    api_key = session.scalar(
        select(UserApiKey).where(
            UserApiKey.key_hash == key_hash,
            UserApiKey.is_active.is_(True),
        )
    )

    if api_key is None:
        return False

    # Check expiration if set
    if api_key.expires_at and api_key.expires_at < datetime.now(timezone.utc):
        return False

    # Record usage
    try:
        api_key.last_used_at = datetime.now(timezone.utc)
        session.commit()
    except Exception:
        session.rollback()

    return True


def check_mcp_auth(session: Session, token: str | None = None) -> None:
    """Checks authentication for an MCP tool execution.

    Raises:
        ToolError: If authentication fails, providing a clear hint on how to obtain a key.
    """
    if not verify_mcp_token(session, token=token):
        raise ToolError(
            "Authentifizierung fehlgeschlagen: Ungültiger oder fehlender Politiklar API-Schlüssel. "
            "Erstelle deinen persönlichen Schlüssel unter http://localhost:3000/konto und hinterlege ihn "
            "als Umgebungsvariable POLITIKLAR_API_KEY in deiner MCP-Client-Konfiguration."
        )

