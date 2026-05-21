"""SQLAlchemy ORM 모델 정의. DB 종류와 무관하게 동작."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# 다대다 조인 테이블: 한 기사가 여러 카테고리에 속할 수 있음.
article_categories = Table(
    "article_categories",
    Base.metadata,
    Column(
        "article_id",
        Integer,
        ForeignKey("articles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "category_id",
        Integer,
        ForeignKey("categories.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(1024), nullable=False, unique=True)
    language: Mapped[str] = mapped_column(String(8), nullable=False)  # 'ko' / 'en'
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    articles: Mapped[list["Article"]] = relationship(back_populates="source")

    def __repr__(self) -> str:
        return f"<Source {self.id} {self.language} {self.name!r}>"


class Category(Base):
    """미리 정의된 분류 카테고리. group은 sky/land/sea, slug는 bird/space 등."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    group: Mapped[str] = mapped_column(String(16), nullable=False)  # sky / land / sea
    label_ko: Mapped[str] = mapped_column(String(64), nullable=False)

    articles: Mapped[list["Article"]] = relationship(
        secondary=article_categories, back_populates="categories"
    )

    def __repr__(self) -> str:
        return f"<Category {self.group}/{self.slug}>"


class Article(Base):
    __tablename__ = "articles"
    __table_args__ = (
        UniqueConstraint("url", name="uq_articles_url"),
        Index("ix_articles_published_at", "published_at"),
        Index("ix_articles_language", "language"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(
        ForeignKey("sources.id", ondelete="CASCADE"), nullable=False, index=True
    )

    title: Mapped[str] = mapped_column(String(1024), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    language: Mapped[str] = mapped_column(String(8), nullable=False)

    fetched_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    source: Mapped[Source] = relationship(back_populates="articles")
    categories: Mapped[list[Category]] = relationship(
        secondary=article_categories, back_populates="articles"
    )

    def __repr__(self) -> str:
        return f"<Article {self.id} [{self.language}] {self.title[:40]!r}>"
