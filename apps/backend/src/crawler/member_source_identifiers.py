"""Verified mappings from external official source identifiers to MDB IDs."""

from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from db.relational.models import BundestagMember, MemberSourceIdentifier, MemberSourceIdentifierEvidence, ParliamentarySpeech

from .bundestag_biography import parse_biography_page
from .fetcher import fetch_document
from .member_importer import _get_or_create_source
from .plenary_speeches import parse_plenary_protocol


PLENARY_SPEAKER_SOURCE_SYSTEM = "bundestag_plenary_speaker"


def verify_plenary_speaker(
    session: Session,
    mdb_id: int,
    speaker_source_id: str,
    biography_evidence_url: str,
    protocol_evidence_url: str,
    verified_by: str,
) -> MemberSourceIdentifier:
    """Record a reviewed official mapping and link matching stored speeches."""
    member = session.scalar(select(BundestagMember).where(BundestagMember.mdb_id == mdb_id))
    if member is None:
        raise ValueError(f"No imported Bundestag member exists for MDB ID {mdb_id}.")

    biography_document = fetch_document(biography_evidence_url)
    biography = parse_biography_page(biography_document.content.decode("utf-8"), biography_document.source.source_url)
    if biography.mdb_id != mdb_id:
        raise ValueError("The biography evidence does not match the supplied MDB ID.")
    protocol_document = fetch_document(protocol_evidence_url)
    protocol = parse_plenary_protocol(protocol_document.content, protocol_document.source.source_url)
    speech_names = {(speech.first_name, speech.last_name) for speech in protocol.speeches if speech.speaker_source_id == speaker_source_id}
    if (biography.first_name, biography.last_name) not in speech_names:
        raise ValueError("The protocol evidence does not identify the biography subject with the supplied speaker ID.")
    biography_source = _get_or_create_source(session, biography_evidence_url, biography_document)
    protocol_source = _get_or_create_source(session, protocol_evidence_url, protocol_document)
    mapping = session.scalar(select(MemberSourceIdentifier).where(
        MemberSourceIdentifier.source_system == PLENARY_SPEAKER_SOURCE_SYSTEM,
        MemberSourceIdentifier.source_identifier == speaker_source_id,
    ))
    if mapping is not None and mapping.member_id != member.id:
        raise ValueError("The speaker source ID is already mapped to another Bundestag member.")
    if mapping is None:
        mapping = MemberSourceIdentifier(
            member_id=member.id,
            source_document_id=biography_source.id,
            source_system=PLENARY_SPEAKER_SOURCE_SYSTEM,
            source_identifier=speaker_source_id,
        )
        session.add(mapping)
        session.flush()

    mapping.source_document_id = biography_source.id
    mapping.verification_status = "verified"
    mapping.verified_at = datetime.now(UTC)
    mapping.verified_by = verified_by
    session.flush()
    for source, evidence_role in ((biography_source, "biography"), (protocol_source, "protocol")):
        evidence = session.scalar(select(MemberSourceIdentifierEvidence).where(
            MemberSourceIdentifierEvidence.member_source_identifier_id == mapping.id,
            MemberSourceIdentifierEvidence.source_document_id == source.id,
        ))
        if evidence is None:
            session.add(MemberSourceIdentifierEvidence(member_source_identifier_id=mapping.id, source_document_id=source.id, evidence_role=evidence_role))
    session.execute(update(ParliamentarySpeech).where(
        ParliamentarySpeech.speaker_source_id == speaker_source_id,
        ParliamentarySpeech.member_id.is_(None),
    ).values(member_id=member.id))
    session.commit()
    return mapping


def find_verified_member_id(session: Session, speaker_source_id: str | None):
    if speaker_source_id is None:
        return None
    return session.scalar(select(MemberSourceIdentifier.member_id).where(
        MemberSourceIdentifier.source_system == PLENARY_SPEAKER_SOURCE_SYSTEM,
        MemberSourceIdentifier.source_identifier == speaker_source_id,
        MemberSourceIdentifier.verification_status == "verified",
    ))