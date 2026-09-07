"""Create member contact points and mandates.

Revision ID: 20260907_05
Revises: 20260907_04
Create Date: 2026-09-07
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260907_05"
down_revision = "20260907_04"
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table(
        "member_contact_points",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("member_id", uuid, sa.ForeignKey("bundestag_members.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_document_id", uuid, sa.ForeignKey("source_documents.id"), nullable=False),
        sa.Column("contact_type", sa.String(100), nullable=False),
        sa.Column("label", sa.String(255), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("content_sha256", sa.String(64), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("member_id", "contact_type", "url", "content_sha256", name="uq_member_contact_point_content"),
    )
    op.create_table(
        "member_mandates",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("member_id", uuid, sa.ForeignKey("bundestag_members.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_document_id", uuid, sa.ForeignKey("source_documents.id"), nullable=False),
        sa.Column("mandate_type", sa.String(100), nullable=False),
        sa.Column("constituency_number", sa.Integer()),
        sa.Column("constituency_name", sa.String(500)),
        sa.Column("constituency_url", sa.Text()),
        sa.Column("start_date", sa.Date()),
        sa.Column("end_date", sa.Date()),
        sa.Column("content_sha256", sa.String(64), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("member_id", "content_sha256", name="uq_member_mandate_content"),
    )


def downgrade() -> None:
    op.drop_table("member_mandates")
    op.drop_table("member_contact_points")