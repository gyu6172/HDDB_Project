"""저장된 기사를 사람이 읽기 좋은 텍스트로 출력/내보내기."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from .db import SessionLocal
from .models import Article, Category, Source
from .text import clean_for_display


def _fmt_dt(dt: datetime | None) -> str:
    return dt.strftime("%Y-%m-%d %H:%M") if dt else "-"


def _fmt_categories(cats: Iterable[Category]) -> str:
    items = sorted(cats, key=lambda c: (c.group, c.slug))
    if not items:
        return "(없음)"
    return ", ".join(f"{c.group}/{c.slug}({c.label_ko})" for c in items)


def fetch_articles(
    *,
    language: str | None = None,
    source: str | None = None,
    category: str | None = None,
    group: str | None = None,
    limit: int = 20,
) -> list[Article]:
    with SessionLocal() as session:
        stmt = (
            select(Article)
            .options(joinedload(Article.source), selectinload(Article.categories))
            .order_by(Article.published_at.desc().nullslast(), Article.id.desc())
            .limit(limit)
        )
        if language:
            stmt = stmt.where(Article.language == language)
        if source:
            stmt = stmt.join(Source).where(Source.name.like(f"%{source}%"))
        if category or group:
            stmt = stmt.join(Article.categories)
            if category:
                stmt = stmt.where(Category.slug == category)
            if group:
                stmt = stmt.where(Category.group == group)
        return list(session.scalars(stmt).unique())


def render_articles(articles: Iterable[Article], *, full: bool = False) -> str:
    """기사를 사람이 읽기 좋은 텍스트 블록으로 변환."""
    blocks: list[str] = []
    for a in articles:
        body = clean_for_display(a.content)
        if not full and len(body) > 400:
            body = body[:400].rstrip() + " ..."
        blocks.append(
            "\n".join(
                [
                    "=" * 78,
                    f"[{a.language}] {a.title}",
                    f"출처     : {a.source.name}",
                    f"카테고리 : {_fmt_categories(a.categories)}",
                    f"발행일   : {_fmt_dt(a.published_at)}    수집일: {_fmt_dt(a.fetched_at)}",
                    f"URL      : {a.url}",
                    "-" * 78,
                    body or "(본문 없음 — 원문 링크 참고)",
                ]
            )
        )
    return "\n\n".join(blocks) if blocks else "(표시할 기사가 없습니다)"


def export_articles_to_file(text: str, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path
