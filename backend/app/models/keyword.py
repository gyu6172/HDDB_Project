import uuid
from sqlalchemy import Column, String, Text, ForeignKey
from pgvector.sqlalchemy import Vector
from app.core.database import Base


class ArticleKeyword(Base):
    __tablename__ = "article_keywords"

    id         = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id = Column(String, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    text       = Column(Text, nullable=False)
    embedding  = Column(Vector(3072))
