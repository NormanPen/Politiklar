"""RAG and semantic search tools backed by pgvector and RagService."""

from typing import Any
from sqlalchemy.orm import Session

from core.settings import Settings
from rag.service import RagService


def query_bundestag_rag(
    session: Session,
    settings: Settings,
    question: str,
) -> dict[str, Any]:
    """Answers a citizen or parliamentary question strictly grounded in Bundestag records."""
    service = RagService(settings)
    if not service.provider.is_configured:
        return {
            "error": f"AI provider '{service.provider.name}' ist nicht konfiguriert.",
            "is_sufficient_evidence": False,
        }

    response = service.generate_answer(session, question)
    return {
        "question": response.question,
        "answer": response.answer,
        "is_sufficient_evidence": response.is_sufficient_evidence,
        "citations": response.citations,
        "chunks_count": len(response.chunks),
    }


def query_speeches_semantic(
    session: Session,
    settings: Settings,
    query: str,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Performs semantic similarity search against indexed speeches using pgvector cosine distance."""
    service = RagService(settings)
    if not service.provider.is_configured:
        return [
            {"error": f"AI provider '{service.provider.name}' ist nicht konfiguriert."}
        ]

    top_k = max(1, min(limit, 20))
    query_vector = service.get_query_embedding(query)
    chunks = service.search_similar_chunks(session, query_vector, top_k=top_k)

    return [
        {
            "chunk_id": str(c.chunk_id),
            "source_document_id": str(c.source_document_id),
            "speaker": c.metadata.get("speaker_name", "Unbekannt"),
            "locator": c.metadata.get("speech_locator", "Dokument"),
            "similarity_score": c.similarity_score,
            "content": c.content,
        }
        for c in chunks
    ]
