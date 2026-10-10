"""SQL tools for querying Bundestag members, mandates, and named votes."""

from typing import Any
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from db.relational.models import (
    BundestagMember,
    MemberAffiliation,
    MemberMandate,
    MemberProfileSnapshot,
    NamedVote,
    NamedVoteRow,
)


def query_member_profile(session: Session, name_or_mdb_id: str) -> dict[str, Any]:
    """Retrieves official verified Bundestag member profile, mandates, and affiliations."""
    clean_query = name_or_mdb_id.strip()
    if not clean_query:
        return {"found": False, "message": "Suchbegriff darf nicht leer sein."}

    member: BundestagMember | None = None
    if clean_query.isdigit():
        member = session.scalar(
            select(BundestagMember).where(BundestagMember.mdb_id == int(clean_query))
        )

    if member is None:
        # Search by name in MemberProfileSnapshot
        words = clean_query.split()
        if len(words) == 1:
            term = f"%{words[0]}%"
            stmt = (
                select(MemberProfileSnapshot)
                .where(
                    or_(
                        MemberProfileSnapshot.last_name.ilike(term),
                        MemberProfileSnapshot.first_name.ilike(term),
                    )
                )
                .order_by(MemberProfileSnapshot.is_current.desc())
                .limit(1)
            )
        else:
            first_term = f"%{words[0]}%"
            last_term = f"%{words[-1]}%"
            stmt = (
                select(MemberProfileSnapshot)
                .where(
                    or_(
                        MemberProfileSnapshot.first_name.ilike(first_term)
                        & MemberProfileSnapshot.last_name.ilike(last_term),
                        MemberProfileSnapshot.last_name.ilike(first_term)
                        & MemberProfileSnapshot.first_name.ilike(last_term),
                    )
                )
                .order_by(MemberProfileSnapshot.is_current.desc())
                .limit(1)
            )
        snapshot = session.scalar(stmt)
        if snapshot:
            member = session.scalar(
                select(BundestagMember).where(BundestagMember.id == snapshot.member_id)
            )

    if not member:
        return {
            "found": False,
            "query": name_or_mdb_id,
            "message": f"Kein Abgeordneter gefunden für: '{name_or_mdb_id}'",
        }

    # Fetch latest profile snapshot
    current_snapshot = session.scalar(
        select(MemberProfileSnapshot)
        .where(MemberProfileSnapshot.member_id == member.id)
        .order_by(MemberProfileSnapshot.is_current.desc(), MemberProfileSnapshot.observed_at.desc())
        .limit(1)
    )

    # Fetch mandates
    mandates = session.scalars(
        select(MemberMandate)
        .where(MemberMandate.member_id == member.id)
        .order_by(MemberMandate.observed_at.desc())
    ).all()

    # Fetch affiliations (Nebentätigkeiten / Rollen)
    affiliations = session.scalars(
        select(MemberAffiliation)
        .where(MemberAffiliation.member_id == member.id)
        .order_by(MemberAffiliation.category.asc())
    ).all()

    first_name = current_snapshot.first_name if current_snapshot else None
    last_name = current_snapshot.last_name if current_snapshot else "Unbekannt"
    full_name = f"{first_name} {last_name}".strip() if first_name else last_name

    mandates_list = [
        {
            "mandate_type": m.mandate_type,
            "constituency_number": m.constituency_number,
            "constituency_name": m.constituency_name,
        }
        for m in mandates
    ]

    affiliations_list = [
        {
            "category": a.category,
            "organization": a.organization_name,
            "role": a.role_name,
        }
        for a in affiliations
    ]

    return {
        "found": True,
        "mdb_id": member.mdb_id,
        "name": full_name,
        "parliamentary_group": current_snapshot.parliamentary_group if current_snapshot else None,
        "occupation": current_snapshot.occupation if current_snapshot else None,
        "mandates": mandates_list,
        "affiliations": affiliations_list,
    }


def query_named_vote(session: Session, title_or_id: str) -> dict[str, Any]:
    """Retrieves official voting results for a specific named vote in the Bundestag."""
    clean_query = title_or_id.strip()
    if not clean_query:
        return {"found": False, "message": "Suchbegriff darf nicht leer sein."}

    vote: NamedVote | None = None
    if clean_query.isdigit():
        vote = session.scalar(
            select(NamedVote).where(NamedVote.vote_number == int(clean_query)).limit(1)
        )

    if not vote:
        vote = session.scalar(
            select(NamedVote)
            .where(NamedVote.title.ilike(f"%{clean_query}%"))
            .order_by(NamedVote.retrieved_at.desc())
            .limit(1)
        )

    if not vote:
        return {
            "found": False,
            "query": title_or_id,
            "message": f"Keine namentliche Abstimmung gefunden für: '{title_or_id}'",
        }

    # Aggregate outcomes across rows
    rows = session.scalars(
        select(NamedVoteRow).where(NamedVoteRow.named_vote_id == vote.id)
    ).all()

    outcome_counts = {
        "yes": 0,
        "no": 0,
        "abstained": 0,
        "not_voted": 0,
        "invalid": 0,
        "total": len(rows),
    }
    fractions: dict[str, dict[str, int]] = {}

    for row in rows:
        out = row.outcome if row.outcome in outcome_counts else "not_voted"
        outcome_counts[out] += 1

        fraction = row.parliamentary_group or "Fraktionslos"
        if fraction not in fractions:
            fractions[fraction] = {"yes": 0, "no": 0, "abstained": 0, "not_voted": 0, "invalid": 0}
        if out in fractions[fraction]:
            fractions[fraction][out] += 1

    return {
        "found": True,
        "electoral_term": vote.electoral_term,
        "sitting_number": vote.sitting_number,
        "vote_number": vote.vote_number,
        "title": vote.title,
        "results_summary": outcome_counts,
        "fraction_breakdown": fractions,
    }


def list_recent_named_votes(session: Session, limit: int = 10, electoral_term: int = 21) -> list[dict[str, Any]]:
    """Lists recently registered named votes for an electoral term."""
    votes = session.scalars(
        select(NamedVote)
        .where(NamedVote.electoral_term == electoral_term)
        .order_by(NamedVote.sitting_number.desc(), NamedVote.vote_number.desc())
        .limit(max(1, min(limit, 50)))
    ).all()

    return [
        {
            "electoral_term": v.electoral_term,
            "sitting_number": v.sitting_number,
            "vote_number": v.vote_number,
            "title": v.title,
        }
        for v in votes
    ]
