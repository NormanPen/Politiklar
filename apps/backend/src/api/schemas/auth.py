"""Pydantic schemas for authentication, users, API keys, and user favorites."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OAuthSyncRequest(BaseModel):
    """Payload sent by frontend authentication handler to register or sync an OAuth identity."""

    provider: str = Field(..., description="OAuth provider name, e.g. 'google', 'microsoft'")
    provider_account_id: str = Field(..., description="Provider's unique user identifier (e.g. Google sub)")
    email: str = Field(..., max_length=255, description="User's email address")
    name: str | None = Field(default=None, description="User's full name or display name")
    avatar_url: str | None = Field(default=None, description="URL of user profile avatar")


class UserResponse(BaseModel):
    """Public representation of a user profile."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    name: str | None
    avatar_url: str | None
    role: str
    is_active: bool
    created_at: datetime


class ApiKeyCreateRequest(BaseModel):
    """Request to generate a new API / MCP access key."""

    name: str = Field(..., min_length=1, max_length=100, description="Label for the API key, e.g. 'MCP Server'")


class ApiKeyCreateResponse(BaseModel):
    """Response returned upon API key generation containing the raw secret once."""

    id: UUID
    name: str
    key_prefix: str
    raw_key: str = Field(..., description="Plaintext secret token, displayed only once upon creation")
    created_at: datetime


class ApiKeyInfo(BaseModel):
    """Metadata of an existing API key without secret values."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    key_prefix: str
    is_active: bool
    last_used_at: datetime | None
    expires_at: datetime | None
    created_at: datetime


class FavoriteCreateRequest(BaseModel):
    """Request to bookmark an entity (e.g. bundestag_member, dossier)."""

    entity_type: str = Field(..., description="Type of entity, e.g. 'bundestag_member', 'dossier'")
    entity_id: UUID = Field(..., description="ID of the bookmarked entity")


class FavoriteResponse(BaseModel):
    """Response representing a user favorite."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    entity_type: str
    entity_id: UUID
    created_at: datetime
