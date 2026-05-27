"""add confidence indexes on articles

sort=confidence / min_confidence 필터 쿼리 가속.

Revision ID: 002
Revises: 001
Create Date: 2026-05-25
"""
from alembic import op


revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "ix_articles_confidence",
        "articles",
        ["confidence"],
    )
    op.create_index(
        "ix_articles_category_confidence",
        "articles",
        ["category_id", "confidence"],
    )


def downgrade():
    op.drop_index("ix_articles_category_confidence", table_name="articles")
    op.drop_index("ix_articles_confidence", table_name="articles")
