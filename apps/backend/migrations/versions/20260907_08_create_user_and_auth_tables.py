"""Create users, user_accounts, user_api_keys, and user_favorites tables.

Revision ID: 20260907_08
Revises: 20260907_07
Create Date: 2026-09-11
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260907_08"
down_revision = "20260907_07"
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)

    # 1. users table
    op.create_table(
        "users",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("email_verified", sa.DateTime(timezone=True), nullable=True),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column("hashed_password", sa.String(255), nullable=True),
        sa.Column("role", sa.String(20), nullable=False, server_default="user"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("role IN ('user', 'admin')", name="ck_user_role"),
        sa.UniqueConstraint("email", name="uq_user_email"),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # 2. user_accounts table (OAuth identities: Google, Microsoft, GitHub etc.)
    op.create_table(
        "user_accounts",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("user_id", uuid, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("provider_account_id", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("provider", "provider_account_id", name="uq_user_provider_account"),
    )
    op.create_index("ix_user_accounts_user_id", "user_accounts", ["user_id"])

    # 3. user_api_keys table (for MCP server and API token authorization)
    op.create_table(
        "user_api_keys",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("user_id", uuid, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("key_hash", sa.String(64), nullable=False),
        sa.Column("key_prefix", sa.String(16), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("key_hash", name="uq_user_api_key_hash"),
    )
    op.create_index("ix_user_api_keys_user_id", "user_api_keys", ["user_id"])

    # 4. user_favorites table (for bookmarking politicians, dossiers, laws)
    op.create_table(
        "user_favorites",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("user_id", uuid, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", uuid, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("user_id", "entity_type", "entity_id", name="uq_user_favorites_entity"),
    )
    op.create_index("ix_user_favorites_user_id", "user_favorites", ["user_id"])


def downgrade() -> None:
    op.drop_table("user_favorites")
    op.drop_table("user_api_keys")
    op.drop_table("user_accounts")
    op.drop_table("users")
