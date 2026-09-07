"""Create independently sourced member affiliations.

Revision ID: 20260907_03
Revises: 20260907_02
Create Date: 2026-09-07
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260907_03"
down_revision = "20260907_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "member_affiliations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("member_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bundestag_members.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("source_documents.id"), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("organization_name", sa.String(500), nullable=False),
        sa.Column("organization_url", sa.Text()),
        sa.Column("role_name", sa.String(255)),
        sa.Column("start_date", sa.Date()),
        sa.Column("end_date", sa.Date()),
        sa.Column("content_sha256", sa.String(64), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("member_id", "content_sha256", name="uq_member_affiliation_content"),
    )


def downgrade() -> None:
    op.drop_table("member_affiliations")