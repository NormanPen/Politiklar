"""Pydantic schemas for RAG endpoints."""

from pydantic import BaseModel, Field


class RagQueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000, description="User question about parliamentary activities.")
    top_k: int | None = Field(default=5, ge=1, le=20, description="Max number of relevant chunks to retrieve.")


class CitationItem(BaseModel):
    source_document_id: str
    speech_id: str | None = None
    locator: str
    speaker: str
    similarity_score: float


class ChunkItem(BaseModel):
    chunk_id: str
    source_document_id: str
    content: str
    similarity_score: float


class RagQueryResponse(BaseModel):
    question: str
    answer: str
    is_sufficient_evidence: bool
    citations: list[CitationItem]
    chunks: list[ChunkItem]
