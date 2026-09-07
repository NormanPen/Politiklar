"""Parliamentary plenary speeches router endpoints."""

from math import ceil
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from api.dependencies import get_db_session
from api.schemas.common import PaginatedResponse, PaginationMeta
from api.schemas.speeches import SpeechDetail, SpeechSummary
from db.relational.models import ParliamentarySpeech

router = APIRouter(prefix="/api/v1/speeches", tags=["Parliamentary Speeches"])


@router.get("", response_model=PaginatedResponse[SpeechSummary], summary="List plenary speeches")
def list_speeches(
    term: int | None = Query(None, description="Filter by electoral term (Wahlperiode)"),
    sitting: int | None = Query(None, description="Filter by plenary sitting number"),
    group: str | None = Query(None, description="Filter by parliamentary group (Fraktion)"),
    speaker: str | None = Query(None, description="Search speaker by name or speaker ID"),
    member_id: UUID | None = Query(None, description="Filter by verified member ID"),
    search: str | None = Query(None, description="Search query within speech text"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db_session),
) -> PaginatedResponse[SpeechSummary]:
    """List parliamentary speeches from official plenary protocols with search and filters."""
    query = select(ParliamentarySpeech)

    if term is not None:
        query = query.where(ParliamentarySpeech.electoral_term == term)
    if sitting is not None:
        query = query.where(ParliamentarySpeech.sitting_number == sitting)
    if group is not None:
        query = query.where(ParliamentarySpeech.parliamentary_group.ilike(f"%{group}%"))
    if member_id is not None:
        query = query.where(ParliamentarySpeech.member_id == member_id)
    if speaker is not None:
        pat = f"%{speaker}%"
        query = query.where(
            or_(
                ParliamentarySpeech.speaker_source_id.ilike(pat),
                ParliamentarySpeech.first_name.ilike(pat),
                ParliamentarySpeech.last_name.ilike(pat),
            )
        )
    if search is not None:
        query = query.where(ParliamentarySpeech.text.ilike(f"%{search}%"))

    count_stmt = select(func.count()).select_from(query.subquery())
    total = db.scalar(count_stmt) or 0

    offset = (page - 1) * page_size
    paginated_query = (
        query.order_by(
            ParliamentarySpeech.electoral_term.desc(),
            ParliamentarySpeech.sitting_number.desc(),
            ParliamentarySpeech.speech_locator.asc(),
        )
        .offset(offset)
        .limit(page_size)
    )
    speeches = db.scalars(paginated_query).all()

    items: list[SpeechSummary] = []
    for speech in speeches:
        preview = speech.text[:250].strip() + ("..." if len(speech.text) > 250 else "")
        items.append(
            SpeechSummary(
                id=speech.id,
                electoral_term=speech.electoral_term,
                sitting_number=speech.sitting_number,
                speech_locator=speech.speech_locator,
                speaker_source_id=speech.speaker_source_id,
                first_name=speech.first_name,
                last_name=speech.last_name,
                parliamentary_group=speech.parliamentary_group,
                member_id=speech.member_id,
                text_preview=preview,
                observed_at=speech.observed_at,
            )
        )

    total_pages = ceil(total / page_size) if total > 0 else 1

    return PaginatedResponse(
        items=items,
        meta=PaginationMeta(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        ),
    )


@router.get("/{speech_id}", response_model=SpeechDetail, summary="Get full parliamentary speech text")
def get_speech_by_id(
    speech_id: UUID,
    db: Session = Depends(get_db_session),
) -> SpeechDetail:
    """Retrieve complete official verbatim text and provenance references for a single speech."""
    speech = db.scalars(select(ParliamentarySpeech).where(ParliamentarySpeech.id == speech_id)).first()
    if not speech:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parliamentary speech with ID '{speech_id}' not found.",
        )
    return SpeechDetail.model_validate(speech)
