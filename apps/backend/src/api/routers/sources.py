"""Source document provenance endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.dependencies import get_db_session
from api.schemas.sources import SourceDocumentDetail
from db.relational.models import SourceDocument

router = APIRouter(prefix="/api/v1/sources", tags=["Sources"])


@router.get("/{source_id}", response_model=SourceDocumentDetail, summary="Get source document by ID")
def get_source_document(
    source_id: UUID,
    db: Session = Depends(get_db_session),
) -> SourceDocumentDetail:
    """Retrieve official source document provenance record by its unique ID."""
    stmt = select(SourceDocument).where(SourceDocument.id == source_id)
    doc = db.scalars(stmt).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source document with ID '{source_id}' not found.",
        )
    return SourceDocumentDetail.model_validate(doc)


@router.get("/by-sha256/{content_sha256}", response_model=SourceDocumentDetail, summary="Get source document by SHA256")
def get_source_document_by_sha256(
    content_sha256: str,
    db: Session = Depends(get_db_session),
) -> SourceDocumentDetail:
    """Retrieve official source document provenance record by content SHA256 hash."""
    stmt = select(SourceDocument).where(SourceDocument.content_sha256 == content_sha256)
    doc = db.scalars(stmt).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source document with SHA256 '{content_sha256}' not found.",
        )
    return SourceDocumentDetail.model_validate(doc)
