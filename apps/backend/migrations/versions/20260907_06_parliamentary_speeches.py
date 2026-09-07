"""Create official parliamentary speech schema.

Revision ID: 20260907_06
Revises: 20260907_05
Create Date: 2026-09-07
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260907_06"
down_revision = "20260907_05"
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table(
        "parliamentary_speeches",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("protocol_source_document_id", uuid, sa.ForeignKey("source_documents.id"), nullable=False),
        sa.Column("member_id", uuid, sa.ForeignKey("bundestag_members.id", ondelete="SET NULL")),
        sa.Column("electoral_term", sa.Integer(), nullable=False),
        sa.Column("sitting_number", sa.Integer(), nullable=False),
        sa.Column("speech_locator", sa.String(100), nullable=False),
        sa.Column("speaker_source_id", sa.String(100)),
        sa.Column("first_name", sa.String(255)),
        sa.Column("last_name", sa.String(255)),
        sa.Column("parliamentary_group", sa.String(255)),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("content_sha256", sa.String(64), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("protocol_source_document_id", "speech_locator", "content_sha256", name="uq_parliamentary_speech_content"),
    )


def downgrade() -> None:
    op.drop_table("parliamentary_speeches")