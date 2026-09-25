"""RagService coordinating vector retrieval and grounded generation."""

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from langchain_google_genai import ChatGoogleGenerativeAI
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.settings import Settings
from db.relational.models import DocumentChunk
from .embeddings import get_embeddings_client
from .prompts import INSUFFICIENT_EVIDENCE_MESSAGE, RAG_SYSTEM_PROMPT


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: UUID
    source_document_id: UUID
    speech_id: UUID | None
    chunk_index: int
    content: str
    metadata: dict[str, Any]
    similarity_score: float


@dataclass(frozen=True)
class RagResponse:
    question: str
    answer: str
    is_sufficient_evidence: bool
    citations: list[dict[str, Any]]
    chunks: list[RetrievedChunk]


class RagService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def get_query_embedding(self, query_text: str) -> list[float]:
        """Generates embedding vector for a user query."""
        client = get_embeddings_client(self.settings)
        return client.embed_query(query_text)

    def search_similar_chunks(
        self,
        session: Session,
        query_vector: list[float],
        top_k: int | None = None,
        score_threshold: float | None = None,
    ) -> list[RetrievedChunk]:
        """Searches similar document chunks using pgvector cosine distance."""
        limit = top_k or self.settings.rag_top_k
        min_score = score_threshold or self.settings.rag_score_threshold

        distance_col = DocumentChunk.embedding.cosine_distance(query_vector).label("distance")
        stmt = (
            select(DocumentChunk, distance_col)
            .order_by(distance_col.asc())
            .limit(limit)
        )
        results = session.execute(stmt).all()

        retrieved: list[RetrievedChunk] = []
        for chunk, distance in results:
            similarity = 1.0 - float(distance)
            if similarity >= min_score:
                retrieved.append(
                    RetrievedChunk(
                        chunk_id=chunk.id,
                        source_document_id=chunk.source_document_id,
                        speech_id=chunk.speech_id,
                        chunk_index=chunk.chunk_index,
                        content=chunk.chunk_content,
                        metadata=chunk.metadata_json or {},
                        similarity_score=round(similarity, 4),
                    )
                )
        return retrieved

    def generate_answer(
        self,
        session: Session,
        question: str,
        query_vector: list[float] | None = None,
    ) -> RagResponse:
        """Retrieves evidence and generates an evidence-grounded answer."""
        if query_vector is None:
            query_vector = self.get_query_embedding(question)

        chunks = self.search_similar_chunks(session, query_vector)
        if not chunks:
            return RagResponse(
                question=question,
                answer=INSUFFICIENT_EVIDENCE_MESSAGE,
                is_sufficient_evidence=False,
                citations=[],
                chunks=[],
            )

        context_parts = []
        citations = []
        for c in chunks:
            source_id = str(c.source_document_id)
            locator = c.metadata.get("speech_locator", "Dokument")
            speaker = c.metadata.get("speaker_name", "Unbekannt")
            context_parts.append(
                f"[Quelle: {source_id}, {locator} (Redner: {speaker})]\n{c.content}"
            )
            citations.append({
                "source_document_id": source_id,
                "speech_id": str(c.speech_id) if c.speech_id else None,
                "locator": locator,
                "speaker": speaker,
                "similarity_score": c.similarity_score,
            })

        context_str = "\n\n".join(context_parts)
        prompt = RAG_SYSTEM_PROMPT.format(
            insufficient_evidence_message=INSUFFICIENT_EVIDENCE_MESSAGE,
            context=context_str,
            question=question,
        )

        llm = ChatGoogleGenerativeAI(
            model=self.settings.gemini_chat_model,
            google_api_key=self.settings.gemini_api_key,
            temperature=0.0,
        )
        response = llm.invoke(prompt)
        answer_text = str(response.content).strip()

        is_sufficient = INSUFFICIENT_EVIDENCE_MESSAGE not in answer_text

        return RagResponse(
            question=question,
            answer=answer_text,
            is_sufficient_evidence=is_sufficient,
            citations=citations,
            chunks=chunks,
        )
