"""RSS 크롤러: 활성 소스에서 최신 기사를 가져와 DB에 저장."""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from time import mktime

import feedparser
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import SessionLocal
from .models import Article, Source

logger = logging.getLogger(__name__)

MAX_ENTRIES = int(os.getenv("MAX_ENTRIES_PER_SOURCE", "50") or 0)
HTTP_TIMEOUT = int(os.getenv("HTTP_TIMEOUT", "15"))


@dataclass
class CrawlResult:
    source: str
    fetched: int
    inserted: int
    skipped: int
    error: str | None = None


def _parse_published(entry) -> datetime | None:
    """RSS 엔트리에서 발행일을 안전하게 파싱."""
    for key in ("published_parsed", "updated_parsed", "created_parsed"):
        value = entry.get(key)
        if value:
            try:
                return datetime.fromtimestamp(mktime(value), tz=timezone.utc).replace(tzinfo=None)
            except (TypeError, ValueError, OverflowError):
                continue
    return None


def _pick_content(entry) -> str:
    """본문 후보 중 가장 풍부한 것을 선택. RSS는 보통 요약만 제공."""
    if entry.get("content"):
        parts = [c.get("value", "") for c in entry["content"] if c.get("value")]
        if parts:
            return "\n\n".join(parts)
    return entry.get("summary") or entry.get("description") or ""


def _crawl_source(session: Session, source: Source) -> CrawlResult:
    logger.info("Fetching %s (%s)", source.name, source.url)

    parsed = feedparser.parse(source.url, request_headers={"User-Agent": "news-crawler/1.0"})
    if parsed.bozo and not parsed.entries:
        return CrawlResult(source.name, 0, 0, 0, error=str(parsed.bozo_exception))

    entries = parsed.entries
    if MAX_ENTRIES > 0:
        entries = entries[:MAX_ENTRIES]

    inserted = skipped = 0
    for entry in entries:
        url = (entry.get("link") or "").strip()
        title = (entry.get("title") or "").strip()
        if not url or not title:
            skipped += 1
            continue

        exists = session.scalar(select(Article.id).where(Article.url == url))
        if exists:
            skipped += 1
            continue

        session.add(
            Article(
                source_id=source.id,
                title=title[:1024],
                content=_pick_content(entry),
                url=url[:2048],
                published_at=_parse_published(entry),
                language=source.language,
            )
        )
        inserted += 1

    session.commit()
    return CrawlResult(source.name, len(entries), inserted, skipped)


def crawl_all(language: str | None = None) -> list[CrawlResult]:
    """등록된 활성 소스를 순회하며 최신 기사를 수집한다."""
    results: list[CrawlResult] = []
    with SessionLocal() as session:
        stmt = select(Source).where(Source.active.is_(True))
        if language:
            stmt = stmt.where(Source.language == language)
        sources = session.scalars(stmt).all()

        if not sources:
            logger.warning("No active sources found. Run `init` or `sync-sources` first.")
            return results

        for source in sources:
            try:
                results.append(_crawl_source(session, source))
            except Exception as exc:  # noqa: BLE001 - 한 소스 실패가 전체를 막지 않도록
                logger.exception("Failed to crawl %s", source.name)
                session.rollback()
                results.append(CrawlResult(source.name, 0, 0, 0, error=str(exc)))
    return results
