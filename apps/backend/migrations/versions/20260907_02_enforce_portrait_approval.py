"""Enforce portrait approval safeguards.

Revision ID: 20260907_02
Revises: 20260907_01
Create Date: 2026-09-07
"""

from alembic import op
import sqlalchemy as sa


revision = "20260907_02"
down_revision = "20260907_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_member_image_candidate_approved_license",
        "member_image_candidates",
        "status != 'approved' OR license_approved",
    )
    op.create_index(
        "uq_member_approved_image",
        "member_image_candidates",
        ["member_id"],
        unique=True,
        postgresql_where=sa.text("status = 'approved'"),
    )


def downgrade() -> None:
    op.drop_index("uq_member_approved_image", table_name="member_image_candidates")
    op.drop_constraint(
        "ck_member_image_candidate_approved_license",
        "member_image_candidates",
        type_="check",
    )