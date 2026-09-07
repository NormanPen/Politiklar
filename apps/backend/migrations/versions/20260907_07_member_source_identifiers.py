"""Create verified member source identifier mappings.

Revision ID: 20260907_07
Revises: 20260907_06
Create Date: 2026-09-07
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260907_07"
down_revision = "20260907_06"
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table(
        "member_source_identifiers",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("member_id", uuid, sa.ForeignKey("bundestag_members.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_document_id", uuid, sa.ForeignKey("source_documents.id"), nullable=False),
        sa.Column("source_system", sa.String(100), nullable=False),
        sa.Column("source_identifier", sa.String(255), nullable=False),
        sa.Column("verification_status", sa.String(20), nullable=False, server_default="pending_review"),
        sa.Column("verified_at", sa.DateTime(timezone=True)),
        sa.Column("verified_by", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("verification_status IN ('pending_review', 'verified', 'rejected')", name="ck_member_source_identifier_status"),
        sa.UniqueConstraint("source_system", "source_identifier", name="uq_member_source_identifier"),
    )
    op.create_table(
        "member_source_identifier_evidence",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("member_source_identifier_id", uuid, sa.ForeignKey("member_source_identifiers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_document_id", uuid, sa.ForeignKey("source_documents.id"), nullable=False),
        sa.Column("evidence_role", sa.String(50), nullable=False),
        sa.UniqueConstraint("member_source_identifier_id", "source_document_id", name="uq_member_source_identifier_evidence"),
    )


def downgrade() -> None:
    op.drop_table("member_source_identifier_evidence")
    op.drop_table("member_source_identifiers")