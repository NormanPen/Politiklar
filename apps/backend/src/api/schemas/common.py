"""Common schemas and pagination models."""

from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class PaginationMeta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int = Field(..., description="Total count of items matching the query")
    page: int = Field(..., ge=1, description="Current page number (1-based)")
    page_size: int = Field(..., ge=1, le=100, description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")


class PaginatedResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(from_attributes=True)

    items: list[T]
    meta: PaginationMeta


class SourceDocumentRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    publisher: str
    resolved_url: str
    content_sha256: str
    retrieved_at: datetime


class ErrorResponse(BaseModel):
    detail: str
