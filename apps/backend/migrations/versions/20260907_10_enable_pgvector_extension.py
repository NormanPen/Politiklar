"""Enable pgvector extension.

Revision ID: 20260907_10
Revises: 20260907_09
Create Date: 2026-09-16
"""

from alembic import op

revision = "20260907_10"
down_revision = "20260907_09"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS vector;")
