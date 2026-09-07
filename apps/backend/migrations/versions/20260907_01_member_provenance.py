"""Create member and source provenance schema.

Revision ID: 20260907_01
Revises:
Create Date: 2026-09-07
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260907_01"
down_revision = None
branch_labels = None
depends_on = None


UUID = postgresql.UUID(as_uuid=True)


def upgrade() -> None:
    op.create_table(
        "source_documents",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("publisher", sa.String(200), nullable=False),
        sa.Column("requested_url", sa.Text(), nullable=False),
        sa.Column("resolved_url", sa.Text(), nullable=False),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("content_type", sa.String(255), nullable=False),
        sa.Column("content_sha256", sa.String(64), nullable=False),
        sa.Column("retrieval_tool", sa.String(100), nullable=False),
        sa.Column("snapshot_location", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("resolved_url", "content_sha256", name="uq_source_document_content"),
    )
    op.create_table(
        "bundestag_members",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("mdb_id", sa.Integer(), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_table(
        "member_terms",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("member_id", UUID, sa.ForeignKey("bundestag_members.id", ondelete="CASCADE"), nullable=False),
        sa.Column("electoral_term", sa.Integer(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("source_document_id", UUID, sa.ForeignKey("source_documents.id"), nullable=False),
        sa.UniqueConstraint("member_id", "electoral_term", name="uq_member_electoral_term"),
    )
    op.create_table(
        "member_external_identifiers",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("member_id", UUID, sa.ForeignKey("bundestag_members.id", ondelete="CASCADE"), nullable=False),
        sa.Column("namespace", sa.String(100), nullable=False),
        sa.Column("identifier", sa.String(255), nullable=False),
        sa.Column("verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("source_document_id", UUID, sa.ForeignKey("source_documents.id"), nullable=False),
        sa.UniqueConstraint("namespace", "identifier", name="uq_external_identifier"),
    )
    op.create_table(
        "member_profile_snapshots",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("member_id", UUID, sa.ForeignKey("bundestag_members.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_document_id", UUID, sa.ForeignKey("source_documents.id"), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("first_name", sa.String(255)),
        sa.Column("last_name", sa.String(255), nullable=False),
        sa.Column("name_prefix", sa.String(255)),
        sa.Column("occupation", sa.String(500)),
        sa.Column("parliamentary_group", sa.String(255)),
        sa.Column("content_sha256", sa.String(64), nullable=False),
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.UniqueConstraint("member_id", "content_sha256", name="uq_member_profile_content"),
    )
    op.create_table(
        "member_offices",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("member_id", UUID, sa.ForeignKey("bundestag_members.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_document_id", UUID, sa.ForeignKey("source_documents.id"), nullable=False),
        sa.Column("office_type", sa.String(20), nullable=False),
        sa.Column("label", sa.String(255)),
        sa.Column("raw_address", sa.Text(), nullable=False),
        sa.Column("content_sha256", sa.String(64), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("office_type IN ('bundestag', 'constituency')", name="ck_member_office_type"),
        sa.UniqueConstraint("member_id", "office_type", "raw_address", "content_sha256", name="uq_member_office_content"),
    )
    op.create_table(
        "member_external_profiles",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("member_id", UUID, sa.ForeignKey("bundestag_members.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_document_id", UUID, sa.ForeignKey("source_documents.id"), nullable=False),
        sa.Column("platform", sa.String(100), nullable=False),
        sa.Column("raw_label", sa.String(255), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("content_sha256", sa.String(64), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("member_id", "url", "content_sha256", name="uq_member_external_profile_content"),
    )
    op.create_table(
        "member_image_candidates",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("member_id", UUID, sa.ForeignKey("bundestag_members.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_document_id", UUID, sa.ForeignKey("source_documents.id"), nullable=False),
        sa.Column("wikidata_qid", sa.String(32)),
        sa.Column("commons_file_page_url", sa.Text(), nullable=False),
        sa.Column("media_url", sa.Text(), nullable=False),
        sa.Column("commons_filename", sa.String(500), nullable=False),
        sa.Column("commons_sha1", sa.String(40)),
        sa.Column("author", sa.Text()),
        sa.Column("attribution_text", sa.Text()),
        sa.Column("license_name", sa.String(100)),
        sa.Column("license_url", sa.Text()),
        sa.Column("license_approved", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending_review"),
        sa.Column("reviewed_at", sa.DateTime(timezone=True)),
        sa.Column("reviewed_by", sa.String(255)),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("status IN ('pending_review', 'approved', 'rejected')", name="ck_member_image_candidate_status"),
        sa.CheckConstraint("license_approved IN (true, false)", name="ck_member_image_candidate_license_approved"),
        sa.UniqueConstraint("member_id", "commons_file_page_url", name="uq_member_commons_file"),
    )
    op.create_index("ix_member_image_candidates_status", "member_image_candidates", ["status"])


def downgrade() -> None:
    op.drop_index("ix_member_image_candidates_status", table_name="member_image_candidates")
    op.drop_table("member_image_candidates")
    op.drop_table("member_external_profiles")
    op.drop_table("member_offices")
    op.drop_table("member_profile_snapshots")
    op.drop_table("member_external_identifiers")
    op.drop_table("member_terms")
    op.drop_table("bundestag_members")
    op.drop_table("source_documents")