"""HDDB 크롤러 서비스 진입점.

FastAPI 라우터/스케줄러에서 호출되어 RSS 소스를 가져와 메인 DB(articles)에
기사를 저장한다. 실제 구현은 `app.services.Crawler.news_crawler` 모듈에 있다.
"""
from __future__ import annotations

import logging
from typing import Any

from app.services.Crawler.news_crawler.classifier import (
    OllamaClassifier,
    OllamaUnavailable,
)
from app.services.Crawler.news_crawler.crawler import crawl_all
from app.services.Crawler.news_crawler.seed import sync_categories

logger = logging.getLogger(__name__)


def ensure_categories_seeded() -> tuple[int, int]:
    """categories/subcategories 가 비어 있으면 시드한다.

    Returns (categories_added, subcategories_added).
    """
    return sync_categories()


def run_crawl(language: str | None = None) -> dict[str, Any]:
    """등록된 RSS 소스에서 자연 관련 기사를 수집해 DB에 저장한다.

    Ollama 서버가 준비돼 있지 않으면 분류 단계 실패로 ok=False 를 반환한다.
    """
    try:
        classifier = OllamaClassifier()
    except OllamaUnavailable as exc:
        logger.warning("Ollama 사용 불가, 크롤링 건너뜀: %s", exc)
        return {"ok": False, "error": str(exc), "results": []}

    results = crawl_all(language=language, classifier=classifier)
    return {
        "ok": True,
        "total_new": sum(r.inserted for r in results),
        "total_prefiltered": sum(r.prefiltered for r in results),
        "ollama_calls": classifier.call_count,
        "model": classifier.model_name,
        "results": [
            {
                "source": r.source,
                "fetched": r.fetched,
                "inserted": r.inserted,
                "skipped": r.skipped,
                "prefiltered": r.prefiltered,
                "error": r.error,
            }
            for r in results
        ],
    }
