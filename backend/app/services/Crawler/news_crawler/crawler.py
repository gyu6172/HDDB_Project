"""RSS 크롤러: sources.yaml 의 소스에서 최신 기사를 가져와 Ollama LLM 으로 분류 후
메인 프로젝트 DB(articles 테이블)에 저장한다.

자연 관련(하늘/땅/바다) 카테고리 중 하나에 매칭되는 기사만 저장한다.
분류기는 가장 적합한 단일 카테고리와 confidence(0.0~1.0) 를 함께 반환하며,
이 confidence 값은 articles.confidence 컬럼에 저장된다.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from time import mktime

import feedparser
from sqlalchemy import select
from sqlalchemy.orm import Session

from .classifier import OllamaClassifier, passes_prefilter
from .db import SessionLocal
from .models import Article, Subcategory
from .seed import load_sources_from_yaml
from .text import strip_tags
from app.services.embedder import embed_article

logger = logging.getLogger(__name__)

MAX_ENTRIES = int(os.getenv("MAX_ENTRIES_PER_SOURCE", "50") or 0)
MAX_ARTICLES_TOTAL = int(os.getenv("MAX_ARTICLES_TOTAL", "50") or 0)
HTTP_TIMEOUT = int(os.getenv("HTTP_TIMEOUT", "15"))


@dataclass
class CrawlResult:
    source: str
    fetched: int
    inserted: int
    skipped: int
    prefiltered: int = 0
    error: str | None = None


def _parse_published(entry) -> datetime | None:
    for key in ("published_parsed", "updated_parsed", "created_parsed"):
        value = entry.get(key)
        if value:
            try:
                return datetime.fromtimestamp(mktime(value), tz=timezone.utc).replace(tzinfo=None)
            except (TypeError, ValueError, OverflowError):
                continue
    return None


def _pick_content(entry) -> str:
    if entry.get("content"):
        parts = [c.get("value", "") for c in entry["content"] if c.get("value")]
        if parts:
            return "\n\n".join(parts)
    return entry.get("summary") or entry.get("description") or ""


def _plain_text(html_text: str) -> str:
    return strip_tags(html_text, replacement=" ")


def _pick_thumbnail(entry) -> str | None:
    """RSS 엔트리에서 썸네일 URL 추출 시도."""
    for key in ("media_thumbnail", "media_content"):
        media = entry.get(key)
        if isinstance(media, list) and media:
            url = media[0].get("url")
            if url:
                return url
    for link in entry.get("links", []) or []:
        if link.get("rel") == "enclosure" and (link.get("type") or "").startswith("image"):
            href = link.get("href")
            if href:
                return href
    return None


def _load_subcategory_map(session: Session) -> dict[str, Subcategory]:
    """subcategory.key -> Subcategory."""
    return {sc.key: sc for sc in session.scalars(select(Subcategory)).all()}


def _crawl_source(
    session: Session,
    source_name: str,
    source_url: str,
    language: str,
    classifier: OllamaClassifier,
    sub_map: dict[str, Subcategory],
    remaining_budget: int,
) -> CrawlResult:
    logger.info("Fetching %s (%s)", source_name, source_url)

    if remaining_budget <= 0:
        return CrawlResult(source_name, 0, 0, 0)

    parsed = feedparser.parse(
        source_url, request_headers={"User-Agent": "news-crawler/1.0"}
    )
    if parsed.bozo and not parsed.entries:
        return CrawlResult(source_name, 0, 0, 0, error=str(parsed.bozo_exception))

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

        exists = session.scalar(
            select(Article.id).where(Article.original_url == url)
        )
        if exists:
            skipped += 1
            continue

        raw_content = _pick_content(entry)
        plain = _plain_text(raw_content)

        if not passes_prefilter(title, plain):
            prefiltered += 1
            continue

        result = classifier.classify(title, plain)
        if not result.matched or result.slug not in sub_map:
            logger.debug("분류 결과 없음, 제외: %s", title[:60])
            skipped += 1
            continue

        primary = sub_map[result.slug]
        # confidence 는 0.0~1.0 범위로 보장됨 (classifier._coerce_confidence).
        confidence = max(0.0, min(1.0, float(result.confidence)))

        article = Article(
            title=title[:1024],
            original_url=url,
            original_content=raw_content,
            source=source_name,
            source_lang=language,
            published_at=_parse_published(entry),
            thumbnail_url=_pick_thumbnail(entry),
            category_id=primary.category_id,
            subcategory_id=primary.id,
            confidence=confidence,
        )
        session.add(article)
        session.flush()
        try:
            embed_article(article.id, article.title, None, session)
        except Exception:
            logger.warning("임베딩 실패, 기사는 저장됨: %s", title[:60])
        inserted += 1
        logger.info(
            "저장: [%s conf=%.2f] %s",
            result.slug, confidence, title[:60],
        )

    session.commit()
    return CrawlResult(
        source_name, len(entries), inserted, skipped, prefiltered=prefiltered
    )


def crawl_all(
    language: str | None = None,
    classifier: OllamaClassifier | None = None,
) -> list[CrawlResult]:
    """sources.yaml 의 소스를 순회하며 자연 관련 기사만 수집한다.

    총 신규 저장 수는 MAX_ARTICLES_TOTAL(기본 50)을 넘지 않는다.
    """
    results: list[CrawlResult] = []
    if classifier is None:
        classifier = OllamaClassifier()
    logger.info("Ollama 모델: %s", classifier.model_name)

    sources = load_sources_from_yaml()
    if language:
        sources = [s for s in sources if (s.get("language") or "").lower() == language]
    if not sources:
        logger.warning("등록된 소스가 없습니다. config/sources.yaml 을 확인하세요.")
        return results

    with SessionLocal() as session:
        sub_map = _load_subcategory_map(session)
        if not sub_map:
            logger.error(
                "subcategories 테이블이 비어 있습니다. `init` 을 먼저 실행하세요."
            )
            return results

        total_inserted = 0
        for src in sources:
            budget = (
                MAX_ARTICLES_TOTAL - total_inserted
                if MAX_ARTICLES_TOTAL > 0
                else 10**9
            )
            name = (src.get("name") or "").strip()
            url = (src.get("url") or "").strip()
            lang = (src.get("language") or "en").strip().lower()
            if not name or not url:
                continue
            if budget <= 0:
                results.append(CrawlResult(name, 0, 0, 0))
                continue
            try:
                result = _crawl_source(
                    session, name, url, lang, classifier, sub_map, budget
                )
                results.append(result)
                total_inserted += result.inserted
            except Exception as exc:  # noqa: BLE001
                logger.exception("Failed to crawl %s", name)
                session.rollback()
                results.append(CrawlResult(name, 0, 0, 0, error=str(exc)))
    return results
