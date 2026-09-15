"""Create verification_tokens table for Double-Opt-In registration.

Revision ID: 20260907_09
Revises: 20260907_08
Create Date: 2026-09-15
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260907_09"
down_revision = "20260907_08"
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)

    op.create_table(
        "verification_tokens",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("token", sa.String(255), nullable=False),
        sa.Column("user_id", uuid, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("token", name="uq_verification_token"),
    )
    op.create_index("ix_verification_tokens_token", "verification_tokens", ["token"])
    op.create_index("ix_verification_tokens_user_id", "verification_tokens", ["user_id"])


def downgrade() -> None:
    op.drop_table("verification_tokens")
