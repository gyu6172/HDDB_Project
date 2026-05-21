import uuid
from sqlalchemy import CheckConstraint, Column, DateTime, Float, ForeignKey, Index, JSON, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Article(Base):
    __tablename__ = "articles"
    __table_args__ = (
        CheckConstraint("source_lang IN ('ko', 'en')", name="ck_articles_source_lang"),
        CheckConstraint(
            "confidence IS NULL OR (confidence >= 0 AND confidence <= 1)",
            name="ck_articles_confidence_range",
        ),
        Index("ix_articles_category_id", "category_id"),
        Index("ix_articles_subcategory_id", "subcategory_id"),
        Index("ix_articles_published_at", "published_at"),
    )

    id                = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title             = Column(String, nullable=False)
    original_url      = Column(String, unique=True, nullable=False)
    original_content  = Column(String)
    source_lang       = Column(String)   # "ko" | "en"
    source            = Column(String)
    published_at      = Column(DateTime)
    thumbnail_url     = Column(String)
    category_id       = Column(String, ForeignKey("categories.id"), nullable=False)
    subcategory_id    = Column(String, ForeignKey("subcategories.id"), nullable=False)
    one_line_summary  = Column(String)
    card_summary      = Column(String)
    paragraph_summary = Column(JSON)     # [{paragraph_index, original_text, summary}]
    confidence        = Column(Float)
    created_at        = Column(DateTime, server_default=func.now())

    category_rel      = relationship("Category", back_populates="articles")
    subcategory_rel   = relationship("Subcategory", back_populates="articles")
