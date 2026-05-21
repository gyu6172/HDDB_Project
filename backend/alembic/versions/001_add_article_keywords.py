"""add article_keywords table

Revision ID: 001
Revises:
Create Date: 2026-05-21
"""
from alembic import op

revision = "001"
down_revision = "5f6112faa479"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("""
        CREATE TABLE article_keywords (
            id         VARCHAR PRIMARY KEY,
            article_id VARCHAR NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
            text       TEXT NOT NULL,
            embedding  vector(3072)
        )
    """)
    op.execute("""
        CREATE INDEX article_keywords_embedding_idx
        ON article_keywords
        USING hnsw (embedding vector_cosine_ops)
    """)


def downgrade():
    op.execute("DROP TABLE IF EXISTS article_keywords")
