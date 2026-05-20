"""저장된 기사를 사람이 읽기 좋은 텍스트로 출력/내보내기."""
from __future__ import annotations

import html
import re
from datetime import datetime
from pathlib import Path
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from .db import SessionLocal
from .models import Article, Source

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"[ \t]+")
_BLANK_RE = re.compile(r"\n{3,}")


def _strip_html(text: str) -> str:
    """RSS content/summary 에 포함된 HTML 태그 제거."""
    if not text:
        return ""
    text = _TAG_RE.sub("", text)
    text = html.unescape(text)
    text = _WS_RE.sub(" ", text)
    text = _BLANK_RE.sub("\n\n", text)
    return text.strip()


def _fmt_dt(dt: datetime | None) -> str:
    return dt.strftime("%Y-%m-%d %H:%M") if dt else "-"


def fetch_articles(
    *,
    language: str | None = None,
    source: str | None = None,
    limit: int = 20,
) -> list[Article]:
    with SessionLocal() as session:
        stmt = (
            select(Article)
            .options(joinedload(Article.source))
            .order_by(Article.published_at.desc().nullslast(), Article.id.desc())
            .limit(limit)
        )
        if language:
            stmt = stmt.where(Article.language == language)
        if source:
            stmt = stmt.join(Source).where(Source.name.like(f"%{source}%"))
        return list(session.scalars(stmt).unique())


def render_articles(articles: Iterable[Article], *, full: bool = False) -> str:
    """기사를 사람이 읽기 좋은 텍스트 블록으로 변환."""
    blocks: list[str] = []
    for a in articles:
        body = _strip_html(a.content)
        if not full and len(body) > 400:
            body = body[:400].rstrip() + " ..."
        blocks.append(
            "\n".join(
                [
                    "=" * 78,
                    f"[{a.language}] {a.title}",
                    f"출처   : {a.source.name}",
                    f"발행일 : {_fmt_dt(a.published_at)}    수집일: {_fmt_dt(a.fetched_at)}",
                    f"URL    : {a.url}",
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
