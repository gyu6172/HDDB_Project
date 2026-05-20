import uuid
from sqlalchemy import Column, String, DateTime, Float, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class Article(Base):
    __tablename__ = "articles"

    id                = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title             = Column(String, nullable=False)
    original_url      = Column(String, unique=True, nullable=False)
    original_content  = Column(String)
    source_lang       = Column(String)   # "ko" | "en"
    source            = Column(String)
    published_at      = Column(DateTime)
    thumbnail_url     = Column(String)
    category          = Column(String)   # "sky" | "land" | "sea"
    subcategory       = Column(String)
    one_line_summary  = Column(String)
    card_summary      = Column(String)
    paragraph_summary = Column(JSON)     # [{paragraph_index, original_text, summary}]
    confidence        = Column(Float)
    created_at        = Column(DateTime, server_default=func.now())
