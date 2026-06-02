"""기존 articles.original_content 에 섞여 있는 HTML 태그/엔티티를 제거하여
사람이 읽기 좋은 평문으로 정규화한다. 다른 컬럼은 일절 변경하지 않는다.
일회성 백필 스크립트. 실행 후 삭제해도 무방.

사용:
    python backfill_clean_original_content.py            # 전체 실행
    python backfill_clean_original_content.py --dry-run  # 변경 없이 미리 보기
    python backfill_clean_original_content.py --limit 5  # 앞 5건만 처리 (검증용)
"""
from __future__ import annotations

import argparse
import logging
import sys

import app.models.article  # noqa: F401  - relationship 해석용
import app.models.category  # noqa: F401
import app.models.keyword   # noqa: F401
from app.core.database import SessionLocal
from app.models.article import Article
from app.services.Crawler.news_crawler.text import clean_for_display

BATCH_COMMIT = 100

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("backfill-clean")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="DB 에 쓰지 않고 변경 예정 건수만 출력")
    parser.add_argument("--limit", type=int, default=0,
                        help="처리 건수 상한 (0=무제한, 검증용)")
    args = parser.parse_args()

    with SessionLocal() as s:
        q = (
            s.query(Article)
            .filter(Article.original_content.isnot(None))
            .order_by(Article.created_at.asc())
        )
        articles = q.limit(args.limit).all() if args.limit > 0 else q.all()

        total = len(articles)
        log.info("대상: %d 건  (dry_run=%s)", total, args.dry_run)
        if total == 0:
            return 0

        changed = 0
        unchanged = 0
        for i, art in enumerate(articles, 1):
            original = art.original_content or ""
            cleaned = clean_for_display(original)
            if cleaned == original:
                unchanged += 1
                continue

            if args.dry_run:
                changed += 1
                if changed <= 3:
                    log.info("[preview %d] %s", changed, (art.title or "")[:60])
                    log.info("  before: %s", original[:120].replace("\n", " "))
                    log.info("  after : %s", cleaned[:120].replace("\n", " "))
                continue

            art.original_content = cleaned
            changed += 1

            if changed % 50 == 0:
                log.info("[%d/%d] changed=%d", i, total, changed)

            if changed % BATCH_COMMIT == 0:
                s.commit()

        if not args.dry_run:
            s.commit()
        log.info("완료: changed=%d  unchanged=%d  total=%d", changed, unchanged, total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
