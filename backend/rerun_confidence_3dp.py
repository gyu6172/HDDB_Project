"""confidence > 0.0 인 기존 기사들(141건)을 재분류하여 confidence 를 3자리 정밀도로 갱신.

정책:
- backfill_confidence.py 와 동일하게 articles.confidence 컬럼만 갱신.
  category_id / subcategory_id 는 절대 수정하지 않는다.
- no_match (confidence=0.0) 기사는 대상에서 제외 (0.000 이라 갱신할 의미가 없음).
- 새 분류기가 이번에도 None 을 돌려주면(=no_match) 그 값을 그대로 받아 0.0 으로 덮어쓴다.
  (드물지만 가능: 프롬프트가 살짝 강화되어 일부가 no_match 로 빠질 수 있음)
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
log = logging.getLogger("rerun3dp")


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
            .filter(Article.confidence > 0.0)
            .order_by(Article.created_at.asc())
            .all()
        )
        total = len(articles)
        log.info("대상(매칭됨, confidence>0.0): %d 건", total)
        if total == 0:
            return 0

        updated = 0
        precision3 = 0   # 새 confidence 가 셋째 자리까지 의미값 (round_3 != round_2)
        new_no_match = 0
        agree = 0
        disagree = 0

        for i, art in enumerate(articles, 1):
            old_conf = float(art.confidence) if art.confidence is not None else 0.0

            plain = strip_tags(art.original_content or "", replacement=" ")
            result = classifier.classify(art.title or "", plain)
            new_conf = max(0.0, min(1.0, float(result.confidence)))

            art.confidence = new_conf  # 이 줄만 변경 (category_id 는 손대지 않음)
            updated += 1

            if round(new_conf, 3) != round(new_conf, 2):
                precision3 += 1

            stored_slug = sub_id_to_slug.get(art.subcategory_id)
            if result.slug is None:
                new_no_match += 1
                tag = "NO_MATCH(new)"
            elif result.slug == stored_slug:
                agree += 1
                tag = "agree"
            else:
                disagree += 1
                tag = f"disagree(stored={stored_slug}, picked={result.slug})"

            log.info(
                "[%d/%d] %.2f → %.3f  %s  %s",
                i, total, old_conf, new_conf, tag, (art.title or "")[:60],
            )

            if i % BATCH_COMMIT == 0:
                s.commit()

        s.commit()
        log.info(
            "완료: updated=%d  3dp_meaningful=%d  agree=%d  disagree=%d  "
            "new_no_match=%d  (Ollama 호출=%d)",
            updated, precision3, agree, disagree, new_no_match,
            classifier.call_count,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
