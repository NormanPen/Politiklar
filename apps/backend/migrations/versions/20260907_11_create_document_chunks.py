"""Create document_chunks table with pgvector embedding and HNSW index.

Revision ID: 20260907_11
Revises: 20260907_10
Create Date: 2026-09-25
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

revision = "20260907_11"
down_revision = "20260907_10"
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table(
        "document_chunks",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("source_document_id", uuid, sa.ForeignKey("source_documents.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("speech_id", uuid, sa.ForeignKey("parliamentary_speeches.id", ondelete="CASCADE"), nullable=True),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("chunk_content", sa.Text(), nullable=False),
        sa.Column("content_sha256", sa.String(64), nullable=False),
        sa.Column("embedding", Vector(768), nullable=False),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("source_document_id", "chunk_index", "content_sha256", name="uq_document_chunk_identity"),
    )
    op.create_index(
        "ix_document_chunks_source_document_id",
        "document_chunks",
        ["source_document_id"],
    )
    op.create_index(
        "ix_document_chunks_speech_id",
        "document_chunks",
        ["speech_id"],
    )
    op.create_index(
        "ix_document_chunks_embedding",
        "document_chunks",
        ["embedding"],
        postgresql_using="hnsw",
        postgresql_with={"m": 16, "ef_construction": 64},
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )


def downgrade() -> None:
    op.drop_index("ix_document_chunks_embedding", table_name="document_chunks")
    op.drop_index("ix_document_chunks_speech_id", table_name="document_chunks")
    op.drop_index("ix_document_chunks_source_document_id", table_name="document_chunks")
    op.drop_table("document_chunks")
