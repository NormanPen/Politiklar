"""Source document schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SourceDocumentDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    publisher: str
    requested_url: str
    resolved_url: str
    retrieved_at: datetime
    status_code: int
    content_type: str
    content_sha256: str
    retrieval_tool: str
    snapshot_location: str | None = None
    created_at: datetime = Field(..., description="Ingestion timestamp")
