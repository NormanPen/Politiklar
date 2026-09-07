"""Named vote response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class VoteBreakdown(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    yes: int = 0
    no: int = 0
    abstained: int = 0
    not_voted: int = 0
    invalid: int = 0
    unknown: int = 0
    total: int = 0


class NamedVoteSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    electoral_term: int
    sitting_number: int
    vote_number: int
    title: str | None = None
    retrieved_at: datetime
    source_document_id: UUID
    breakdown: VoteBreakdown = Field(default_factory=VoteBreakdown)


class NamedVoteRowSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    member_id: UUID | None = None
    first_name: str | None = None
    last_name: str | None = None
    parliamentary_group: str | None = None
    raw_outcome: str
    outcome: str
    remark: str | None = None


class NamedVoteDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    electoral_term: int
    sitting_number: int
    vote_number: int
    title: str | None = None
    retrieved_at: datetime
    source_document_id: UUID
    breakdown: VoteBreakdown = Field(default_factory=VoteBreakdown)
    rows: list[NamedVoteRowSchema] = Field(default_factory=list)
