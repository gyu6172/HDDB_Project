"""RSS 크롤러: 활성 소스에서 최신 기사를 가져와 Ollama LLM 으로 분류 후 DB에 저장.

자연 관련(하늘/땅/바다) 카테고리 중 하나 이상에 매칭되는 기사만 저장한다.
"""
from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from time import mktime

import feedparser
from sqlalchemy import select
from sqlalchemy.orm import Session

from .classifier import OllamaClassifier, passes_prefilter
from .db import SessionLocal
from .models import Article, Category, Source

logger = logging.getLogger(__name__)

# 한 소스에서 후보로 가져올 최대 RSS 엔트리 수 (분류 전).
MAX_ENTRIES = int(os.getenv("MAX_ENTRIES_PER_SOURCE", "50") or 0)
# 한 번의 crawl 호출 전체에서 DB에 신규 저장할 최대 기사 수.
MAX_ARTICLES_TOTAL = int(os.getenv("MAX_ARTICLES_TOTAL", "50") or 0)
HTTP_TIMEOUT = int(os.getenv("HTTP_TIMEOUT", "15"))

_TAG_RE = re.compile(r"<[^>]+>")


@dataclass
class CrawlResult:
    source: str
    fetched: int
    inserted: int
    skipped: int  # 중복 또는 분류 결과 없음으로 제외된 수
    prefiltered: int = 0  # 키워드 사전 필터에서 걸러진 수 (API 미호출)
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


def _plain_text(html_text: str) -> str:
    """분류기 프롬프트에 넣기 전에 HTML 태그를 단순 제거."""
    if not html_text:
        return ""
    return _TAG_RE.sub(" ", html_text)


def _load_category_map(session: Session) -> dict[str, Category]:
    return {c.slug: c for c in session.scalars(select(Category)).all()}


def _crawl_source(
    session: Session,
    source: Source,
    classifier: OllamaClassifier,
    category_map: dict[str, Category],
    remaining_budget: int,
) -> CrawlResult:
    logger.info("Fetching %s (%s)", source.name, source.url)

    if remaining_budget <= 0:
        return CrawlResult(source.name, 0, 0, 0)

    parsed = feedparser.parse(source.url, request_headers={"User-Agent": "news-crawler/1.0"})
    if parsed.bozo and not parsed.entries:
        return CrawlResult(source.name, 0, 0, 0, error=str(parsed.bozo_exception))

    entries = parsed.entries
    if MAX_ENTRIES > 0:
        entries = entries[:MAX_ENTRIES]

    inserted = skipped = prefiltered = 0
    for entry in entries:
        if remaining_budget - inserted <= 0:
            break

        url = (entry.get("link") or "").strip()
        title = (entry.get("title") or "").strip()
        if not url or not title:
            skipped += 1
            continue

        exists = session.scalar(select(Article.id).where(Article.url == url))
        if exists:
            skipped += 1
            continue

        raw_content = _pick_content(entry)
        plain = _plain_text(raw_content)

        # 1차: 키워드 사전 필터 — 명백히 자연 무관이면 API 호출 없이 제외.
        if not passes_prefilter(title, plain):
            prefiltered += 1
            continue

        # 2차: 로컬 LLM(Ollama) 정밀 분류.
        slugs = classifier.classify(title, plain)
        if not slugs:
            logger.debug("분류 결과 없음, 제외: %s", title[:60])
            skipped += 1
            continue

        article = Article(
            source_id=source.id,
            title=title[:1024],
            content=raw_content,
            url=url[:2048],
            published_at=_parse_published(entry),
            language=source.language,
        )
        article.categories = [category_map[s] for s in slugs if s in category_map]
        session.add(article)
        session.flush()
        inserted += 1
        logger.info("저장: [%s] %s", ",".join(slugs), title[:60])

    session.commit()
    return CrawlResult(source.name, len(entries), inserted, skipped, prefiltered=prefiltered)


def crawl_all(
    language: str | None = None,
    classifier: OllamaClassifier | None = None,
) -> list[CrawlResult]:
    """등록된 활성 소스를 순회하며 자연 관련 기사만 수집한다.

    총 신규 저장 수는 MAX_ARTICLES_TOTAL(기본 50)을 넘지 않는다.
    Ollama 로컬 LLM 으로 분류하므로 호출 횟수에는 상한이 없다.
    """
    results: list[CrawlResult] = []
    if classifier is None:
        classifier = OllamaClassifier()
    logger.info("Ollama 모델: %s", classifier.model_name)

    with SessionLocal() as session:
        category_map = _load_category_map(session)
        if not category_map:
            logger.error("categories 테이블이 비어 있습니다. `init` 을 먼저 실행하세요.")
            return results

        stmt = select(Source).where(Source.active.is_(True))
        if language:
            stmt = stmt.where(Source.language == language)
        sources = session.scalars(stmt).all()

        if not sources:
            logger.warning("No active sources found. Run `init` or `sync-sources` first.")
            return results

        total_inserted = 0
        for source in sources:
            budget = (
                MAX_ARTICLES_TOTAL - total_inserted if MAX_ARTICLES_TOTAL > 0 else 10**9
            )
            if budget <= 0:
                results.append(CrawlResult(source.name, 0, 0, 0))
                continue
            try:
                result = _crawl_source(session, source, classifier, category_map, budget)
                results.append(result)
                total_inserted += result.inserted
            except Exception as exc:  # noqa: BLE001 - 한 소스 실패가 전체를 막지 않도록
                logger.exception("Failed to crawl %s", source.name)
                session.rollback()
                results.append(CrawlResult(source.name, 0, 0, 0, error=str(exc)))
    return results
