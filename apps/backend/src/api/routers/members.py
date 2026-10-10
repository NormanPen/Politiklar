"""Bundestag member endpoints."""

from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from api.dependencies import get_db_session, get_settings
from api.schemas.common import PaginatedResponse, PaginationMeta
from api.schemas.rag import ChunkItem, CitationItem, RagQueryRequest, RagQueryResponse
from core.settings import Settings
from rag.service import RagService
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
            tokens = [token.strip() for token in search.split() if token.strip()]
            full_name = func.concat(
                func.coalesce(MemberProfileSnapshot.first_name, ""),
                " ",
                func.coalesce(MemberProfileSnapshot.last_name, ""),
            )
            conds = [
                MemberProfileSnapshot.first_name.ilike(f"%{search}%"),
                MemberProfileSnapshot.last_name.ilike(f"%{search}%"),
                full_name.ilike(f"%{search}%"),
            ]
            for token in tokens:
                conds.append(MemberProfileSnapshot.first_name.ilike(f"%{token}%"))
                conds.append(MemberProfileSnapshot.last_name.ilike(f"%{token}%"))
            query = query.where(or_(*conds))

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


@router.post("/{mdb_id}/ask", response_model=RagQueryResponse, summary="Ask question about a specific Bundestag member")
def ask_member_question(
    mdb_id: int,
    payload: RagQueryRequest,
    db: Session = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> RagQueryResponse:
    """Answers citizen and research questions grounded on the politician's official profile, affiliations, and speeches."""
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

    affiliations = db.scalars(
        select(MemberAffiliation)
        .where(MemberAffiliation.member_id == member.id)
        .order_by(MemberAffiliation.category.asc())
    ).all()

    mandates = db.scalars(
        select(MemberMandate)
        .where(MemberMandate.member_id == member.id)
        .order_by(MemberMandate.mandate_type.asc())
    ).all()

    first_name = profile.first_name if profile else ""
    last_name = profile.last_name if profile else f"MdB {member.mdb_id}"
    full_name = f"{first_name} {last_name}".strip()
    group = profile.parliamentary_group if profile else "Fraktionslos"
    occupation = profile.occupation if profile else "Keine Angabe"

    affil_lines = [f"- {a.role_name or 'Mitglied'}: {a.organization_name}" for a in affiliations]
    mandate_lines = [f"- {m.mandate_type}: {m.constituency_name or 'Landesliste'}" for m in mandates]

    profile_context = f"""[Offizielle Stammdaten zu {full_name} (MdB-ID: {member.mdb_id})]:
- Name: {full_name}
- Fraktion: {group}
- Beruf / Tätigkeit: {occupation}
- Mandate: {", ".join(mandate_lines) if mandate_lines else "Keine gesonderten Mandatsdaten"}
- Funktionen, Gremien & Nebentätigkeiten:
{chr(10).join(affil_lines) if affil_lines else "Keine gesonderten Funktionen verzeichnet"}"""

    service = RagService(settings)
    citations: list[CitationItem] = []
    chunks_items: list[ChunkItem] = []

    # Optional speech chunks from vector search
    speech_context_parts = []
    if service.provider.is_configured:
        try:
            search_query = f"{full_name} {payload.question}"
            query_vector = service.get_query_embedding(search_query)
            chunks = service.search_similar_chunks(db, query_vector, top_k=payload.top_k or 3)
            for c in chunks:
                source_id = str(c.source_document_id)
                locator = c.metadata.get("speech_locator", "Plenarprotokoll")
                speaker = c.metadata.get("speaker_name", "Unbekannt")
                speech_context_parts.append(f"[Quelle: {source_id}, {locator} (Redner: {speaker})]\n{c.content}")
                citations.append(
                    CitationItem(
                        source_document_id=source_id,
                        speech_id=str(c.speech_id) if c.speech_id else None,
                        locator=locator,
                        speaker=speaker,
                        similarity_score=c.similarity_score,
                    )
                )
                chunks_items.append(
                    ChunkItem(
                        chunk_id=str(c.chunk_id),
                        source_document_id=source_id,
                        content=c.content,
                        similarity_score=c.similarity_score,
                    )
                )
        except Exception:
            pass

    full_context = profile_context
    if speech_context_parts:
        full_context += "\n\n" + "\n\n".join(speech_context_parts)

    def _synthesize_profile_facts() -> str:
        q_lower = payload.question.lower()
        if any(w in q_lower for w in ["job", "beruf", "nebentätigkeit", "tätigkeit", "arbeit", "funktion", "gremi"]):
            affil_text = "\n".join(affil_lines) if affil_lines else "Keine gesonderten Nebentätigkeiten verzeichnet."
            return (
                f"Laut den offiziellen Bundestags-Stammdaten zu {full_name} ({group}):\n\n"
                f"• Hauptberuf / Ausbildung: {occupation}\n"
                f"• Funktionen, Gremien & Mandate:\n{affil_text}"
            )
        if any(w in q_lower for w in ["partei", "fraktion"]):
            return f"{full_name} gehört der Fraktion '{group}' an."
        if any(w in q_lower for w in ["wahlkreis", "mandat"]):
            mandate_text = "\n".join(mandate_lines) if mandate_lines else "Über die Landesliste eingezogen."
            return f"Mandatsdaten zu {full_name} ({group}):\n{mandate_text}"

        affil_text = "\n".join(affil_lines) if affil_lines else "Keine gesonderten Nebentätigkeiten verzeichnet."
        return (
            f"Offizielle Angaben des Deutschen Bundestages zu {full_name} ({group}):\n\n"
            f"• Beruf: {occupation}\n"
            f"• Funktionen & Gremien:\n{affil_text}"
        )

    answer_text = ""
    if service.provider.is_configured:
        prompt = f"""Du bist der sachliche, politisch strikt neutrale Assistent für das offizielle Bundestags-Profil von {full_name}.
Beantworte die Bürgerfrage sachlich, neutral und ausschließlich auf Basis der folgenden offiziellen Daten des Deutschen Bundestages.
Erfinde keine Fakten. Wenn die Information in den Daten nicht enthalten ist, weise neutral darauf hin.

Kontext:
{full_context}

Frage: {payload.question}

Antwort:"""
        try:
            answer_text = service.provider.generate_text(prompt)
        except Exception:
            # Fallback to factual synthesis if LLM API call fails or times out
            answer_text = _synthesize_profile_facts()
    else:
        answer_text = _synthesize_profile_facts()

    citations.insert(
        0,
        CitationItem(
            source_document_id=str(profile.source_document_id) if profile and profile.source_document_id else str(member.id),
            speech_id=None,
            locator=f"Bundestag Stammdaten MdB {member.mdb_id}",
            speaker=full_name,
            similarity_score=1.0,
        ),
    )

    return RagQueryResponse(
        question=payload.question,
        answer=answer_text,
        is_sufficient_evidence=True,
        citations=citations,
        chunks=chunks_items,
    )

