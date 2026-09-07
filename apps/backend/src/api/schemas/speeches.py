"""Parliamentary speech response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SpeechSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    electoral_term: int
    sitting_number: int
    speech_locator: str
    speaker_source_id: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    parliamentary_group: str | None = None
    member_id: UUID | None = None
    text_preview: str = Field(..., description="Truncated beginning of the speech")
    observed_at: datetime


class SpeechDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    electoral_term: int
    sitting_number: int
    speech_locator: str
    speaker_source_id: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    parliamentary_group: str | None = None
    member_id: UUID | None = None
    text: str
    protocol_source_document_id: UUID
    observed_at: datetime
