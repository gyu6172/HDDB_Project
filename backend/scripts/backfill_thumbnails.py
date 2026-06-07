#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
articles.thumbnail_url 백필 스크립트.

각 기사 URL에서 og:image를 추출해 thumbnail_url을 보완한다.
- og:image 추출 성공 시: 기존 값과 관계없이 교체 (저해상도 개선 포함)
- 추출 실패 시: 기존 값 유지 (덮어쓰지 않음)

사용법:
    cd backend
    python scripts/backfill_thumbnails.py --dry-run   # 변경 예정 목록만 출력
    python scripts/backfill_thumbnails.py             # 실제 DB 업데이트

옵션:
    --dry-run  DB에 실제로 쓰지 않고 변경 예정 내역만 출력
    --delay    요청 간 딜레이(초, 기본값: 1.5)
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import trafilatura
from sqlalchemy import select, update

from app.core.database import SessionLocal
from app.models.article import Article
import app.models.category  # noqa: F401 — SQLAlchemy mapper 관계 해소용


def _fetch_og_image(url: str) -> str | None:
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return None
        meta = trafilatura.extract_metadata(downloaded)
        return getattr(meta, "image", None) if meta else None
    except Exception:
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description="articles.thumbnail_url 백필")
    ap.add_argument("--dry-run", action="store_true", help="DB에 실제로 쓰지 않고 내역만 출력")
    ap.add_argument("--delay", type=float, default=1.5, help="요청 간 딜레이 초 (기본 1.5)")
    args = ap.parse_args()

    with SessionLocal() as session:
        articles = session.scalars(select(Article)).all()

    print(f"총 {len(articles)}개 기사 처리 시작 (dry_run={args.dry_run})\n")

    updated = skipped = failed = 0

    with SessionLocal() as session:
        for i, article in enumerate(articles, 1):
            og_image = _fetch_og_image(article.original_url)

            if og_image:
                old = article.thumbnail_url or "(없음)"
                if args.dry_run:
                    print(f"[{i:3}/{len(articles)}] UPDATE")
                    print(f"         전: {old[:90]}")
                    print(f"         후: {og_image[:90]}")
                    print(f"         출처: {article.original_url[:70]}")
                    print()
                else:
                    session.execute(
                        update(Article)
                        .where(Article.id == article.id)
                        .values(thumbnail_url=og_image)
                    )
                    print(f"[{i:3}/{len(articles)}] UPDATE [{article.source}] {article.title[:50]}")
                updated += 1
            else:
                status = "SKIP(추출실패)" if not article.thumbnail_url else "SKIP(기존유지)"
                print(f"[{i:3}/{len(articles)}] {status} [{article.source}] {article.title[:50]}")
                if article.thumbnail_url:
                    skipped += 1
                else:
                    failed += 1

            time.sleep(args.delay)

        if not args.dry_run:
            session.commit()

    print("\n========== 결과 ==========")
    print(f"업데이트: {updated}개")
    print(f"기존값 유지: {skipped}개")
    print(f"추출 실패(빈값 유지): {failed}개")
    if args.dry_run:
        print("\n[DRY RUN] DB 변경 없음. 실제 반영은 --dry-run 없이 실행하세요.")


if __name__ == "__main__":
    main()
