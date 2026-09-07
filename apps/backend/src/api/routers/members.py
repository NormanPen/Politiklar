"""Bundestag member endpoints."""

from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from api.dependencies import get_db_session
from api.schemas.common import PaginatedResponse, PaginationMeta
from api.schemas.members import (
    MemberAffiliationSchema,
    MemberContactPointSchema,
    MemberDetail,
    MemberExternalProfileSchema,
    MemberImageSchema,
    MemberMandateSchema,
    MemberOfficeSchema,
    MemberSummary,
    MemberTermSchema,
)
from db.relational.models import (
    BundestagMember,
    MemberAffiliation,
    MemberContactPoint,
    MemberExternalProfile,
    MemberImageCandidate,
    MemberMandate,
    MemberOffice,
    MemberProfileSnapshot,
    MemberTerm,
)

router = APIRouter(prefix="/api/v1/members", tags=["Members"])


@router.get("", response_model=PaginatedResponse[MemberSummary], summary="List members")
def list_members(
    term: int | None = Query(None, description="Filter by electoral term (Wahlperiode)"),
    group: str | None = Query(None, description="Filter by parliamentary group (Fraktion)"),
    search: str | None = Query(None, description="Search query for first name or last name"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db_session),
) -> PaginatedResponse[MemberSummary]:
    """List Bundestag members with optional filtering and pagination."""
    query = select(BundestagMember)

    if term is not None:
        query = query.join(MemberTerm, MemberTerm.member_id == BundestagMember.id).where(
            MemberTerm.electoral_term == term
        )

    if group is not None or search is not None:
        # Join profile snapshots if not already joined
        query = query.join(
            MemberProfileSnapshot,
            (MemberProfileSnapshot.member_id == BundestagMember.id) & (MemberProfileSnapshot.is_current.is_(True)),
        )
        if group is not None:
            query = query.where(MemberProfileSnapshot.parliamentary_group.ilike(f"%{group}%"))
        if search is not None:
            pattern = f"%{search}%"
            query = query.where(
                or_(
                    MemberProfileSnapshot.first_name.ilike(pattern),
                    MemberProfileSnapshot.last_name.ilike(pattern),
                )
            )

    query = query.distinct()

    # Count total matching members
    count_stmt = select(func.count()).select_from(query.subquery())
    total = db.scalar(count_stmt) or 0

    # Paginated query
    offset = (page - 1) * page_size
    paginated_query = query.order_by(BundestagMember.mdb_id.asc()).offset(offset).limit(page_size)
    members = db.scalars(paginated_query).all()

    items: list[MemberSummary] = []
    for member in members:
        # Get current profile
        profile = db.scalars(
            select(MemberProfileSnapshot)
            .where(
                MemberProfileSnapshot.member_id == member.id,
                MemberProfileSnapshot.is_current.is_(True),
            )
            .order_by(MemberProfileSnapshot.observed_at.desc())
        ).first()

        # Get terms
        terms = db.scalars(
            select(MemberTerm.electoral_term)
            .where(MemberTerm.member_id == member.id)
            .order_by(MemberTerm.electoral_term.asc())
        ).all()

        # Get approved image if any
        image = db.scalars(
            select(MemberImageCandidate).where(
                MemberImageCandidate.member_id == member.id,
                MemberImageCandidate.status == "approved",
            )
        ).first()

        items.append(
            MemberSummary(
                id=member.id,
                mdb_id=member.mdb_id,
                first_name=profile.first_name if profile else None,
                last_name=profile.last_name if profile else f"MdB {member.mdb_id}",
                name_prefix=profile.name_prefix if profile else None,
                occupation=profile.occupation if profile else None,
                parliamentary_group=profile.parliamentary_group if profile else None,
                electoral_terms=list(terms),
                image_url=image.media_url if image else None,
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


@router.get("/{mdb_id}", response_model=MemberDetail, summary="Get member details by official MDB ID")
def get_member_by_mdb_id(
    mdb_id: int,
    db: Session = Depends(get_db_session),
) -> MemberDetail:
    """Retrieve full official record, profile snapshot, mandates, and provenance for a single Bundestag member."""
    member = db.scalars(select(BundestagMember).where(BundestagMember.mdb_id == mdb_id)).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bundestag member with MDB ID {mdb_id} not found.",
        )

    profile = db.scalars(
        select(MemberProfileSnapshot)
        .where(
            MemberProfileSnapshot.member_id == member.id,
            MemberProfileSnapshot.is_current.is_(True),
        )
        .order_by(MemberProfileSnapshot.observed_at.desc())
    ).first()

    terms = db.scalars(
        select(MemberTerm)
        .where(MemberTerm.member_id == member.id)
        .order_by(MemberTerm.electoral_term.desc())
    ).all()

    offices = db.scalars(
        select(MemberOffice)
        .where(MemberOffice.member_id == member.id)
        .order_by(MemberOffice.office_type.asc())
    ).all()

    contact_points = db.scalars(
        select(MemberContactPoint)
        .where(MemberContactPoint.member_id == member.id)
        .order_by(MemberContactPoint.contact_type.asc())
    ).all()

    mandates = db.scalars(
        select(MemberMandate)
        .where(MemberMandate.member_id == member.id)
        .order_by(MemberMandate.mandate_type.asc())
    ).all()

    external_profiles = db.scalars(
        select(MemberExternalProfile)
        .where(MemberExternalProfile.member_id == member.id)
        .order_by(MemberExternalProfile.platform.asc())
    ).all()

    affiliations = db.scalars(
        select(MemberAffiliation)
        .where(MemberAffiliation.member_id == member.id)
        .order_by(MemberAffiliation.category.asc())
    ).all()

    approved_image = db.scalars(
        select(MemberImageCandidate).where(
            MemberImageCandidate.member_id == member.id,
            MemberImageCandidate.status == "approved",
        )
    ).first()

    return MemberDetail(
        id=member.id,
        mdb_id=member.mdb_id,
        first_name=profile.first_name if profile else None,
        last_name=profile.last_name if profile else f"MdB {member.mdb_id}",
        name_prefix=profile.name_prefix if profile else None,
        occupation=profile.occupation if profile else None,
        parliamentary_group=profile.parliamentary_group if profile else None,
        observed_at=profile.observed_at if profile else None,
        source_document_id=profile.source_document_id if profile else None,
        image=MemberImageSchema.model_validate(approved_image) if approved_image else None,
        terms=[MemberTermSchema.model_validate(t) for t in terms],
        offices=[MemberOfficeSchema.model_validate(o) for o in offices],
        contact_points=[MemberContactPointSchema.model_validate(c) for c in contact_points],
        mandates=[MemberMandateSchema.model_validate(m) for m in mandates],
        external_profiles=[MemberExternalProfileSchema.model_validate(ep) for ep in external_profiles],
        affiliations=[MemberAffiliationSchema.model_validate(a) for a in affiliations],
    )
