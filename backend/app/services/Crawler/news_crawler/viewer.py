"""저장된 기사를 사람이 읽기 좋은 텍스트로 출력/내보내기."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from .db import SessionLocal
from .models import Article, Category, Subcategory
from .text import clean_for_display


def _fmt_dt(dt: datetime | None) -> str:
    return dt.strftime("%Y-%m-%d %H:%M") if dt else "-"


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
            .options(
                joinedload(Article.category_rel),
                joinedload(Article.subcategory_rel),
            )
            .order_by(Article.published_at.desc().nullslast(), Article.id.desc())
            .limit(limit)
        )
        if language:
            stmt = stmt.where(Article.source_lang == language)
        if source:
            stmt = stmt.where(Article.source.like(f"%{source}%"))
        if category:
            stmt = stmt.join(Article.subcategory_rel).where(Subcategory.key == category)
        if group:
            stmt = stmt.join(Article.category_rel).where(Category.key == group)
        return list(session.scalars(stmt).unique())


def render_articles(articles: Iterable[Article], *, full: bool = False) -> str:
    blocks: list[str] = []
    for a in articles:
        body = clean_for_display(a.original_content or "")
        if not full and len(body) > 400:
            body = body[:400].rstrip() + " ..."
        cat = a.category_rel
        sub = a.subcategory_rel
        cat_label = (
            f"{cat.key}/{sub.key}({sub.label})" if cat and sub else "(없음)"
        )
        blocks.append(
            "\n".join(
                [
                    "=" * 78,
                    f"[{a.source_lang}] {a.title}",
                    f"출처     : {a.source}",
                    f"카테고리 : {cat_label}",
                    f"발행일   : {_fmt_dt(a.published_at)}    수집일: {_fmt_dt(a.created_at)}",
                    f"URL      : {a.original_url}",
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
