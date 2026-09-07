"""Create named vote and raw vote row schema.

Revision ID: 20260907_04
Revises: 20260907_03
Create Date: 2026-09-07
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260907_04"
down_revision = "20260907_03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table(
        "named_votes",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("source_document_id", uuid, sa.ForeignKey("source_documents.id"), nullable=False),
        sa.Column("electoral_term", sa.Integer(), nullable=False),
        sa.Column("sitting_number", sa.Integer(), nullable=False),
        sa.Column("vote_number", sa.Integer(), nullable=False),
        sa.Column("title", sa.Text()),
        sa.Column("content_sha256", sa.String(64), nullable=False),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("electoral_term", "sitting_number", "vote_number", "content_sha256", name="uq_named_vote_content"),
    )
    op.create_table(
        "named_vote_rows",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("named_vote_id", uuid, sa.ForeignKey("named_votes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("member_id", uuid, sa.ForeignKey("bundestag_members.id", ondelete="SET NULL")),
        sa.Column("source_document_id", uuid, sa.ForeignKey("source_documents.id"), nullable=False),
        sa.Column("parliamentary_group", sa.String(255)),
        sa.Column("last_name", sa.String(255)),
        sa.Column("first_name", sa.String(255)),
        sa.Column("title", sa.String(255)),
        sa.Column("display_name", sa.String(500)),
        sa.Column("raw_outcome", sa.String(50), nullable=False),
        sa.Column("outcome", sa.String(20), nullable=False),
        sa.Column("remark", sa.Text()),
        sa.Column("content_sha256", sa.String(64), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("outcome IN ('yes', 'no', 'abstained', 'invalid', 'not_voted', 'unknown')", name="ck_named_vote_row_outcome"),
        sa.UniqueConstraint("named_vote_id", "content_sha256", name="uq_named_vote_row_content"),
    )
    op.create_index("ix_named_vote_rows_member_id", "named_vote_rows", ["member_id"])


def downgrade() -> None:
    op.drop_index("ix_named_vote_rows_member_id", table_name="named_vote_rows")
    op.drop_table("named_vote_rows")
    op.drop_table("named_votes")