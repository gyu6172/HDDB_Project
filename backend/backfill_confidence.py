"""confidence 가 NULL 인 기존 기사에 대해서만 분류기를 재실행하여
articles.confidence 컬럼을 채운다. 다른 컬럼은 일절 변경하지 않는다.
일회성 백필 스크립트. 실행 후 삭제해도 무방.
"""
from __future__ import annotations

import logging
import sys

import app.models.article  # noqa: F401  - relationship 해석용
import app.models.category  # noqa: F401
import app.models.keyword   # noqa: F401
from app.core.database import SessionLocal
from app.models.article import Article
from app.models.category import Subcategory
from app.services.Crawler.news_crawler.classifier import (
    OllamaClassifier,
    OllamaUnavailable,
)
from app.services.Crawler.news_crawler.text import strip_tags

BATCH_COMMIT = 10

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("backfill")


def main() -> int:
    try:
        classifier = OllamaClassifier()
    except OllamaUnavailable as exc:
        print(f"[ERROR] {exc}")
        return 2

    with SessionLocal() as s:
        sub_id_to_slug = {sub.id: sub.key for sub in s.query(Subcategory).all()}

        articles = (
            s.query(Article)
            .filter(Article.confidence.is_(None))
            .order_by(Article.created_at.asc())
            .all()
        )
        total = len(articles)
        log.info("backfill 대상: %d 건", total)
        if total == 0:
            return 0

        updated = 0
        agree = 0
        disagree = 0
        no_match = 0  # 분류기가 자연 카테고리에 매칭 못 함 (confidence=0.0 저장)

        for i, art in enumerate(articles, 1):
            plain = strip_tags(art.original_content or "", replacement=" ")
            result = classifier.classify(art.title or "", plain)
            conf = max(0.0, min(1.0, float(result.confidence)))

            art.confidence = conf  # 이 줄만 변경
            updated += 1

            stored_slug = sub_id_to_slug.get(art.subcategory_id)
            if result.slug is None:
                no_match += 1
                tag = "NO_MATCH"
            elif result.slug == stored_slug:
                agree += 1
                tag = "agree"
            else:
                disagree += 1
                tag = f"disagree(was={stored_slug}, picked={result.slug})"

            log.info(
                "[%d/%d] conf=%.2f %s  %s",
                i, total, conf, tag, (art.title or "")[:60],
            )

            if i % BATCH_COMMIT == 0:
                s.commit()

        s.commit()
        log.info(
            "완료: updated=%d  agree=%d  disagree=%d  no_match=%d  (Ollama 호출=%d)",
            updated, agree, disagree, no_match, classifier.call_count,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
