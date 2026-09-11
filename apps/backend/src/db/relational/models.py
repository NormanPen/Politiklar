"""Evidence-first relational records for Bundestag member ingestion."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from .base import Base


class SourceDocument(Base):
    __tablename__ = "source_documents"
    __table_args__ = (UniqueConstraint("resolved_url", "content_sha256", name="uq_source_document_content"),)

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    publisher: Mapped[str] = mapped_column(String(200))
    requested_url: Mapped[str] = mapped_column(Text)
    resolved_url: Mapped[str] = mapped_column(Text)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status_code: Mapped[int] = mapped_column(Integer)
    content_type: Mapped[str] = mapped_column(String(255))
    content_sha256: Mapped[str] = mapped_column(String(64))
    retrieval_tool: Mapped[str] = mapped_column(String(100))
    snapshot_location: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class BundestagMember(Base):
    __tablename__ = "bundestag_members"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    mdb_id: Mapped[int] = mapped_column(Integer, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MemberTerm(Base):
    __tablename__ = "member_terms"
    __table_args__ = (UniqueConstraint("member_id", "electoral_term", name="uq_member_electoral_term"),)

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    member_id: Mapped[UUID] = mapped_column(ForeignKey("bundestag_members.id", ondelete="CASCADE"))
    electoral_term: Mapped[int] = mapped_column(Integer)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    source_document_id: Mapped[UUID] = mapped_column(ForeignKey("source_documents.id"))


class MemberExternalIdentifier(Base):
    __tablename__ = "member_external_identifiers"
    __table_args__ = (UniqueConstraint("namespace", "identifier", name="uq_external_identifier"),)

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    member_id: Mapped[UUID] = mapped_column(ForeignKey("bundestag_members.id", ondelete="CASCADE"))
    namespace: Mapped[str] = mapped_column(String(100))
    identifier: Mapped[str] = mapped_column(String(255))
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    source_document_id: Mapped[UUID] = mapped_column(ForeignKey("source_documents.id"))


class MemberSourceIdentifier(Base):
    __tablename__ = "member_source_identifiers"
    __table_args__ = (
        CheckConstraint("verification_status IN ('pending_review', 'verified', 'rejected')", name="ck_member_source_identifier_status"),
        UniqueConstraint("source_system", "source_identifier", name="uq_member_source_identifier"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    member_id: Mapped[UUID] = mapped_column(ForeignKey("bundestag_members.id", ondelete="CASCADE"))
    source_document_id: Mapped[UUID] = mapped_column(ForeignKey("source_documents.id"))
    source_system: Mapped[str] = mapped_column(String(100))
    source_identifier: Mapped[str] = mapped_column(String(255))
    verification_status: Mapped[str] = mapped_column(String(20), default="pending_review")
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MemberSourceIdentifierEvidence(Base):
    __tablename__ = "member_source_identifier_evidence"
    __table_args__ = (UniqueConstraint("member_source_identifier_id", "source_document_id", name="uq_member_source_identifier_evidence"),)

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    member_source_identifier_id: Mapped[UUID] = mapped_column(ForeignKey("member_source_identifiers.id", ondelete="CASCADE"))
    source_document_id: Mapped[UUID] = mapped_column(ForeignKey("source_documents.id"))
    evidence_role: Mapped[str] = mapped_column(String(50))


class MemberProfileSnapshot(Base):
    __tablename__ = "member_profile_snapshots"
    __table_args__ = (UniqueConstraint("member_id", "content_sha256", name="uq_member_profile_content"),)

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    member_id: Mapped[UUID] = mapped_column(ForeignKey("bundestag_members.id", ondelete="CASCADE"))
    source_document_id: Mapped[UUID] = mapped_column(ForeignKey("source_documents.id"))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str] = mapped_column(String(255))
    name_prefix: Mapped[str | None] = mapped_column(String(255), nullable=True)
    occupation: Mapped[str | None] = mapped_column(String(500), nullable=True)
    parliamentary_group: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content_sha256: Mapped[str] = mapped_column(String(64))
    is_current: Mapped[bool] = mapped_column(Boolean, default=True)


class MemberOffice(Base):
    __tablename__ = "member_offices"
    __table_args__ = (
        CheckConstraint("office_type IN ('bundestag', 'constituency')", name="ck_member_office_type"),
        UniqueConstraint("member_id", "office_type", "raw_address", "content_sha256", name="uq_member_office_content"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    member_id: Mapped[UUID] = mapped_column(ForeignKey("bundestag_members.id", ondelete="CASCADE"))
    source_document_id: Mapped[UUID] = mapped_column(ForeignKey("source_documents.id"))
    office_type: Mapped[str] = mapped_column(String(20))
    label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    raw_address: Mapped[str] = mapped_column(Text)
    content_sha256: Mapped[str] = mapped_column(String(64))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class MemberContactPoint(Base):
    __tablename__ = "member_contact_points"
    __table_args__ = (UniqueConstraint("member_id", "contact_type", "url", "content_sha256", name="uq_member_contact_point_content"),)

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    member_id: Mapped[UUID] = mapped_column(ForeignKey("bundestag_members.id", ondelete="CASCADE"))
    source_document_id: Mapped[UUID] = mapped_column(ForeignKey("source_documents.id"))
    contact_type: Mapped[str] = mapped_column(String(100))
    label: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(Text)
    content_sha256: Mapped[str] = mapped_column(String(64))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class MemberMandate(Base):
    __tablename__ = "member_mandates"
    __table_args__ = (UniqueConstraint("member_id", "content_sha256", name="uq_member_mandate_content"),)

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    member_id: Mapped[UUID] = mapped_column(ForeignKey("bundestag_members.id", ondelete="CASCADE"))
    source_document_id: Mapped[UUID] = mapped_column(ForeignKey("source_documents.id"))
    mandate_type: Mapped[str] = mapped_column(String(100))
    constituency_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    constituency_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    constituency_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    content_sha256: Mapped[str] = mapped_column(String(64))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class MemberExternalProfile(Base):
    __tablename__ = "member_external_profiles"
    __table_args__ = (UniqueConstraint("member_id", "url", "content_sha256", name="uq_member_external_profile_content"),)

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    member_id: Mapped[UUID] = mapped_column(ForeignKey("bundestag_members.id", ondelete="CASCADE"))
    source_document_id: Mapped[UUID] = mapped_column(ForeignKey("source_documents.id"))
    platform: Mapped[str] = mapped_column(String(100))
    raw_label: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(Text)
    content_sha256: Mapped[str] = mapped_column(String(64))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class MemberAffiliation(Base):
    __tablename__ = "member_affiliations"
    __table_args__ = (UniqueConstraint("member_id", "content_sha256", name="uq_member_affiliation_content"),)

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    member_id: Mapped[UUID] = mapped_column(ForeignKey("bundestag_members.id", ondelete="CASCADE"))
    source_document_id: Mapped[UUID] = mapped_column(ForeignKey("source_documents.id"))
    category: Mapped[str] = mapped_column(String(100))
    organization_name: Mapped[str] = mapped_column(String(500))
    organization_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    role_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    start_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    content_sha256: Mapped[str] = mapped_column(String(64))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class MemberImageCandidate(Base):
    __tablename__ = "member_image_candidates"
    __table_args__ = (
        CheckConstraint("status IN ('pending_review', 'approved', 'rejected')", name="ck_member_image_candidate_status"),
        CheckConstraint("license_approved IN (true, false)", name="ck_member_image_candidate_license_approved"),
        CheckConstraint("status != 'approved' OR license_approved", name="ck_member_image_candidate_approved_license"),
        UniqueConstraint("member_id", "commons_file_page_url", name="uq_member_commons_file"),
        Index("ix_member_image_candidates_status", "status"),
        Index(
            "uq_member_approved_image",
            "member_id",
            unique=True,
            postgresql_where="status = 'approved'",
        ),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    member_id: Mapped[UUID] = mapped_column(ForeignKey("bundestag_members.id", ondelete="CASCADE"))
    source_document_id: Mapped[UUID] = mapped_column(ForeignKey("source_documents.id"))
    wikidata_qid: Mapped[str | None] = mapped_column(String(32), nullable=True)
    commons_file_page_url: Mapped[str] = mapped_column(Text)
    media_url: Mapped[str] = mapped_column(Text)
    commons_filename: Mapped[str] = mapped_column(String(500))
    commons_sha1: Mapped[str | None] = mapped_column(String(40), nullable=True)
    author: Mapped[str | None] = mapped_column(Text, nullable=True)
    attribution_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    license_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    license_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    license_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(20), default="pending_review")
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class NamedVote(Base):
    __tablename__ = "named_votes"
    __table_args__ = (UniqueConstraint("electoral_term", "sitting_number", "vote_number", "content_sha256", name="uq_named_vote_content"),)

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    source_document_id: Mapped[UUID] = mapped_column(ForeignKey("source_documents.id"))
    electoral_term: Mapped[int] = mapped_column(Integer)
    sitting_number: Mapped[int] = mapped_column(Integer)
    vote_number: Mapped[int] = mapped_column(Integer)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_sha256: Mapped[str] = mapped_column(String(64))
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class NamedVoteRow(Base):
    __tablename__ = "named_vote_rows"
    __table_args__ = (
        CheckConstraint("outcome IN ('yes', 'no', 'abstained', 'invalid', 'not_voted', 'unknown')", name="ck_named_vote_row_outcome"),
        UniqueConstraint("named_vote_id", "content_sha256", name="uq_named_vote_row_content"),
        Index("ix_named_vote_rows_member_id", "member_id"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    named_vote_id: Mapped[UUID] = mapped_column(ForeignKey("named_votes.id", ondelete="CASCADE"))
    member_id: Mapped[UUID | None] = mapped_column(ForeignKey("bundestag_members.id", ondelete="SET NULL"), nullable=True)
    source_document_id: Mapped[UUID] = mapped_column(ForeignKey("source_documents.id"))
    parliamentary_group: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    raw_outcome: Mapped[str] = mapped_column(String(50))
    outcome: Mapped[str] = mapped_column(String(20))
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_sha256: Mapped[str] = mapped_column(String(64))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ParliamentarySpeech(Base):
    __tablename__ = "parliamentary_speeches"
    __table_args__ = (UniqueConstraint("protocol_source_document_id", "speech_locator", "content_sha256", name="uq_parliamentary_speech_content"),)

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    protocol_source_document_id: Mapped[UUID] = mapped_column(ForeignKey("source_documents.id"))
    member_id: Mapped[UUID | None] = mapped_column(ForeignKey("bundestag_members.id", ondelete="SET NULL"), nullable=True)
    electoral_term: Mapped[int] = mapped_column(Integer)
    sitting_number: Mapped[int] = mapped_column(Integer)
    speech_locator: Mapped[str] = mapped_column(String(100))
    speaker_source_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    parliamentary_group: Mapped[str | None] = mapped_column(String(255), nullable=True)
    text: Mapped[str] = mapped_column(Text)
    content_sha256: Mapped[str] = mapped_column(String(64))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('user', 'admin')", name="ck_user_role"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email_verified: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(20), default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class UserAccount(Base):
    __tablename__ = "user_accounts"
    __table_args__ = (
        UniqueConstraint("provider", "provider_account_id", name="uq_user_provider_account"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    provider: Mapped[str] = mapped_column(String(50))
    provider_account_id: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class UserApiKey(Base):
    __tablename__ = "user_api_keys"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100))
    key_hash: Mapped[str] = mapped_column(String(64), unique=True)
    key_prefix: Mapped[str] = mapped_column(String(16))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class UserFavorite(Base):
    __tablename__ = "user_favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "entity_type", "entity_id", name="uq_user_favorites_entity"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    entity_type: Mapped[str] = mapped_column(String(50))
    entity_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())