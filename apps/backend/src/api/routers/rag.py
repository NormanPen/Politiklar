"""RAG and semantic search router endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.dependencies import get_db_session, get_settings
from api.schemas.rag import ChunkItem, CitationItem, RagQueryRequest, RagQueryResponse
from core.settings import Settings
from rag.service import RagService

router = APIRouter(prefix="/api/v1/rag", tags=["RAG & Semantic Search"])


@router.post("/ask", response_model=RagQueryResponse, summary="Ask question grounded on parliamentary records")
def ask_question(
    payload: RagQueryRequest,
    db: Session = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> RagQueryResponse:
    """Answers a question strictly grounded on retrieved official Bundestag records."""
    if not settings.gemini_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gemini API is not configured on this server.",
        )
    service = RagService(settings)
    try:
        result = service.generate_answer(db, payload.question)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error querying Gemini RAG service: {str(e)}",
        )

    return RagQueryResponse(
        question=result.question,
        answer=result.answer,
        is_sufficient_evidence=result.is_sufficient_evidence,
        citations=[CitationItem(**c) for c in result.citations],
        chunks=[
            ChunkItem(
                chunk_id=str(c.chunk_id),
                source_document_id=str(c.source_document_id),
                content=c.content,
                similarity_score=c.similarity_score,
            )
            for c in result.chunks
        ],
    )


@router.post("/search", response_model=list[ChunkItem], summary="Semantic search across document chunks")
def semantic_search(
    payload: RagQueryRequest,
    db: Session = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> list[ChunkItem]:
    """Performs semantic similarity search against pgvector without LLM generation."""
    if not settings.gemini_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gemini API is not configured on this server.",
        )
    service = RagService(settings)
    query_vector = service.get_query_embedding(payload.question)
    chunks = service.search_similar_chunks(db, query_vector, top_k=payload.top_k)

    return [
        ChunkItem(
            chunk_id=str(c.chunk_id),
            source_document_id=str(c.source_document_id),
            content=c.content,
            similarity_score=c.similarity_score,
        )
        for c in chunks
    ]
