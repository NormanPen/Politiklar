"""Named votes router endpoints."""

from math import ceil
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from api.dependencies import get_db_session
from api.schemas.common import PaginatedResponse, PaginationMeta
from api.schemas.votes import (
    NamedVoteDetail,
    NamedVoteRowSchema,
    NamedVoteSummary,
    VoteBreakdown,
)
from db.relational.models import NamedVote, NamedVoteRow

router = APIRouter(prefix="/api/v1/votes", tags=["Named Votes"])


def compute_vote_breakdown(vote_id: UUID, db: Session) -> VoteBreakdown:
    stmt = (
        select(NamedVoteRow.outcome, func.count(NamedVoteRow.id))
        .where(NamedVoteRow.named_vote_id == vote_id)
        .group_by(NamedVoteRow.outcome)
    )
    counts = dict(db.execute(stmt).all())
    total = sum(counts.values())
    return VoteBreakdown(
        yes=counts.get("yes", 0),
        no=counts.get("no", 0),
        abstained=counts.get("abstained", 0),
        not_voted=counts.get("not_voted", 0),
        invalid=counts.get("invalid", 0),
        unknown=counts.get("unknown", 0),
        total=total,
    )


@router.get("", response_model=PaginatedResponse[NamedVoteSummary], summary="List named votes")
def list_named_votes(
    term: int | None = Query(None, description="Filter by electoral term (Wahlperiode)"),
    sitting: int | None = Query(None, description="Filter by sitting number (Sitzungsnummer)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db_session),
) -> PaginatedResponse[NamedVoteSummary]:
    """List official Bundestag named votes with aggregate voting statistics."""
    query = select(NamedVote)
    if term is not None:
        query = query.where(NamedVote.electoral_term == term)
    if sitting is not None:
        query = query.where(NamedVote.sitting_number == sitting)

    count_stmt = select(func.count()).select_from(query.subquery())
    total = db.scalar(count_stmt) or 0

    offset = (page - 1) * page_size
    paginated_query = (
        query.order_by(
            NamedVote.electoral_term.desc(),
            NamedVote.sitting_number.desc(),
            NamedVote.vote_number.desc(),
        )
        .offset(offset)
        .limit(page_size)
    )
    votes = db.scalars(paginated_query).all()

    items: list[NamedVoteSummary] = []
    for vote in votes:
        breakdown = compute_vote_breakdown(vote.id, db)
        items.append(
            NamedVoteSummary(
                id=vote.id,
                electoral_term=vote.electoral_term,
                sitting_number=vote.sitting_number,
                vote_number=vote.vote_number,
                title=vote.title,
                retrieved_at=vote.retrieved_at,
                source_document_id=vote.source_document_id,
                breakdown=breakdown,
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


@router.get("/{vote_id}", response_model=NamedVoteDetail, summary="Get named vote details and individual votes")
def get_named_vote_details(
    vote_id: UUID,
    db: Session = Depends(get_db_session),
) -> NamedVoteDetail:
    """Retrieve full named vote results, including verified vote rows and provenance reference."""
    vote = db.scalars(select(NamedVote).where(NamedVote.id == vote_id)).first()
    if not vote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Named vote with ID '{vote_id}' not found.",
        )

    breakdown = compute_vote_breakdown(vote.id, db)

    rows = db.scalars(
        select(NamedVoteRow)
        .where(NamedVoteRow.named_vote_id == vote.id)
        .order_by(
            NamedVoteRow.parliamentary_group.asc().nulls_last(),
            NamedVoteRow.last_name.asc().nulls_last(),
            NamedVoteRow.first_name.asc().nulls_last(),
        )
    ).all()

    return NamedVoteDetail(
        id=vote.id,
        electoral_term=vote.electoral_term,
        sitting_number=vote.sitting_number,
        vote_number=vote.vote_number,
        title=vote.title,
        retrieved_at=vote.retrieved_at,
        source_document_id=vote.source_document_id,
        breakdown=breakdown,
        rows=[NamedVoteRowSchema.model_validate(r) for r in rows],
    )
