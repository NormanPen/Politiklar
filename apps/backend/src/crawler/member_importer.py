"""Idempotent import of a single Bundestag biography page."""

from datetime import datetime
from hashlib import sha256

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from db.relational.models import (
    BundestagMember,
    MemberAffiliation,
    MemberContactPoint,
    MemberExternalProfile,
    MemberMandate,
    MemberOffice,
    MemberProfileSnapshot,
    MemberTerm,
    SourceDocument,
)

from .bundestag_biography import MemberBiography, parse_biography_page
from .fetcher import FetchedDocument, fetch_document


def import_biography(session: Session, url: str, electoral_term: int = 21) -> MemberBiography:
    """Fetch, parse and persist one biography page without duplicate observations."""
    document = fetch_document(url)
    biography = parse_biography_page(document.content.decode("utf-8"), document.source.source_url)
    source = _get_or_create_source(session, url, document)
    member = session.scalar(select(BundestagMember).where(BundestagMember.mdb_id == biography.mdb_id))
    if member is None:
        member = BundestagMember(mdb_id=biography.mdb_id)
        session.add(member)
        session.flush()

    _ensure_term(session, member, source.id, electoral_term)
    _persist_profile(session, member, source.id, biography, document.source.retrieved_at)
    _persist_offices(session, member, source.id, biography, document.source.retrieved_at)
    _persist_contact_points(session, member, source.id, biography, document.source.retrieved_at)
    _persist_mandates(session, member, source.id, biography, document.source.retrieved_at)
    _persist_external_profiles(session, member, source.id, biography, document.source.retrieved_at)
    _persist_affiliations(session, member, source.id, biography, document.source.retrieved_at)
    session.commit()
    return biography


def _get_or_create_source(session: Session, requested_url: str, document: FetchedDocument) -> SourceDocument:
    source = session.scalar(
        select(SourceDocument).where(
            SourceDocument.resolved_url == document.source.source_url,
            SourceDocument.content_sha256 == document.source.content_sha256,
        )
    )
    if source is not None:
        return source
    source = SourceDocument(
        publisher="Deutscher Bundestag",
        requested_url=requested_url,
        resolved_url=document.source.source_url,
        retrieved_at=datetime.fromisoformat(document.source.retrieved_at),
        status_code=document.source.status_code,
        content_type=document.source.content_type,
        content_sha256=document.source.content_sha256,
        retrieval_tool="PolitiklarCrawler/0.1",
        snapshot_location=document.snapshot_location,
    )
    session.add(source)
    session.flush()
    return source


def _ensure_term(session: Session, member: BundestagMember, source_id: object, electoral_term: int) -> None:
    term = session.scalar(select(MemberTerm).where(MemberTerm.member_id == member.id, MemberTerm.electoral_term == electoral_term))
    if term is None:
        session.add(MemberTerm(member_id=member.id, electoral_term=electoral_term, active=True, source_document_id=source_id))


def _persist_profile(session: Session, member: BundestagMember, source_id: object, biography: MemberBiography, retrieved_at: str) -> None:
    exists = session.scalar(select(MemberProfileSnapshot.id).where(MemberProfileSnapshot.member_id == member.id, MemberProfileSnapshot.content_sha256 == biography.content_sha256))
    if exists is not None:
        return
    session.execute(update(MemberProfileSnapshot).where(MemberProfileSnapshot.member_id == member.id).values(is_current=False))
    session.add(MemberProfileSnapshot(
        member_id=member.id,
        source_document_id=source_id,
        observed_at=datetime.fromisoformat(retrieved_at),
        first_name=biography.first_name,
        last_name=biography.last_name,
        name_prefix=biography.name_prefix,
        occupation=biography.occupation,
        parliamentary_group=biography.parliamentary_group,
        content_sha256=biography.content_sha256,
        is_current=True,
    ))


def _persist_offices(session: Session, member: BundestagMember, source_id: object, biography: MemberBiography, retrieved_at: str) -> None:
    for office in biography.offices:
        content_hash = sha256(f"{office.office_type}\0{office.raw_address}".encode()).hexdigest()
        exists = session.scalar(select(MemberOffice.id).where(MemberOffice.member_id == member.id, MemberOffice.content_sha256 == content_hash))
        if exists is None:
            session.add(MemberOffice(member_id=member.id, source_document_id=source_id, office_type=office.office_type, label=office.label, raw_address=office.raw_address, content_sha256=content_hash, observed_at=datetime.fromisoformat(retrieved_at)))


def _persist_contact_points(session: Session, member: BundestagMember, source_id: object, biography: MemberBiography, retrieved_at: str) -> None:
    for contact in biography.contact_points:
        content_hash = sha256(repr(contact).encode()).hexdigest()
        exists = session.scalar(select(MemberContactPoint.id).where(MemberContactPoint.member_id == member.id, MemberContactPoint.content_sha256 == content_hash))
        if exists is None:
            session.add(MemberContactPoint(member_id=member.id, source_document_id=source_id, contact_type=contact.contact_type, label=contact.label, url=contact.url, content_sha256=content_hash, observed_at=datetime.fromisoformat(retrieved_at)))


def _persist_mandates(session: Session, member: BundestagMember, source_id: object, biography: MemberBiography, retrieved_at: str) -> None:
    for mandate in biography.mandates:
        content_hash = sha256(repr(mandate).encode()).hexdigest()
        exists = session.scalar(select(MemberMandate.id).where(MemberMandate.member_id == member.id, MemberMandate.content_sha256 == content_hash))
        if exists is None:
            session.add(MemberMandate(member_id=member.id, source_document_id=source_id, mandate_type=mandate.mandate_type, constituency_number=mandate.constituency_number, constituency_name=mandate.constituency_name, constituency_url=mandate.constituency_url, start_date=mandate.start_date, content_sha256=content_hash, observed_at=datetime.fromisoformat(retrieved_at)))


def _persist_external_profiles(session: Session, member: BundestagMember, source_id: object, biography: MemberBiography, retrieved_at: str) -> None:
    for profile in biography.external_profiles:
        content_hash = sha256(f"{profile.platform}\0{profile.url}".encode()).hexdigest()
        exists = session.scalar(select(MemberExternalProfile.id).where(MemberExternalProfile.member_id == member.id, MemberExternalProfile.content_sha256 == content_hash))
        if exists is None:
            session.add(MemberExternalProfile(member_id=member.id, source_document_id=source_id, platform=profile.platform, raw_label=profile.raw_label, url=profile.url, content_sha256=content_hash, observed_at=datetime.fromisoformat(retrieved_at)))


def _persist_affiliations(session: Session, member: BundestagMember, source_id: object, biography: MemberBiography, retrieved_at: str) -> None:
    for affiliation in biography.affiliations:
        content_hash = sha256(repr(affiliation).encode()).hexdigest()
        exists = session.scalar(select(MemberAffiliation.id).where(MemberAffiliation.member_id == member.id, MemberAffiliation.content_sha256 == content_hash))
        if exists is None:
            session.add(MemberAffiliation(
                member_id=member.id,
                source_document_id=source_id,
                category=affiliation.category,
                organization_name=affiliation.organization_name,
                organization_url=affiliation.organization_url,
                role_name=affiliation.role_name,
                start_date=affiliation.start_date,
                end_date=affiliation.end_date,
                content_sha256=content_hash,
                observed_at=datetime.fromisoformat(retrieved_at),
            ))