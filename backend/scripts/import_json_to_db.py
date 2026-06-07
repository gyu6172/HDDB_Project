#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
크롤링 JSON 파일을 Supabase DB에 삽입하는 스크립트.

사용법:
    cd backend
    python scripts/import_json_to_db.py --input scripts/output/ko_articles_20260605.json
    python scripts/import_json_to_db.py --input scripts/output/ko_articles_20260605.json --dry-run

옵션:
    --input    삽입할 JSON 파일 경로 (필수)
    --dry-run  DB에 실제로 쓰지 않고 내용만 출력
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.article import Article


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def main() -> None:
    ap = argparse.ArgumentParser(description="크롤링 JSON -> Supabase DB 삽입")
    ap.add_argument("--input", required=True, help="크롤링 JSON 파일 경로")
    ap.add_argument("--dry-run", action="store_true", help="DB에 실제로 쓰지 않고 내용만 출력")
    args = ap.parse_args()

    path = Path(args.input)
    if not path.exists():
        print(f"파일 없음: {path}")
        sys.exit(1)

    with open(path, encoding="utf-8") as f:
        articles = json.load(f)

    if not isinstance(articles, list):
        print("JSON 최상위가 리스트여야 합니다.")
        sys.exit(1)

    print(f"총 {len(articles)}개 기사 로드 완료")

    if args.dry_run:
        print("\n[DRY RUN - DB 저장 없음]")
        print(f"{'카테고리':<22} {'확신도':>6}  제목")
        print("-" * 80)
        for a in articles:
            slug = a.get("subcategory_key", "?")
            conf = a.get("confidence", 0)
            title = (a.get("title") or "")[:55]
            print(f"  {slug:<20} {conf:>5.2f}  {title}")
        return

    inserted = skipped = 0
    with SessionLocal() as session:
        for a in articles:
            url = a.get("original_url", "")
            if not url:
                print(f"  SKIP (URL 없음): {a.get('title', '')[:50]}")
                skipped += 1
                continue

            exists = session.scalar(select(Article.id).where(Article.original_url == url))
            if exists:
                print(f"  SKIP (중복): {a.get('title', '')[:55]}")
                skipped += 1
                continue

            article = Article(
                id=a.get("id"),
                title=a.get("title", "")[:1024],
                original_url=url,
                original_content=a.get("original_content"),
                source_lang=a.get("source_lang", "ko"),
                source=a.get("source"),
                published_at=_parse_dt(a.get("published_at")),
                thumbnail_url=a.get("thumbnail_url"),
                category_id=a["category_id"],
                subcategory_id=a["subcategory_id"],
                confidence=a.get("confidence"),
                one_line_summary=a.get("one_line_summary"),
                card_summary=a.get("card_summary"),
                paragraph_summary=a.get("paragraph_summary"),
            )
            session.add(article)
            inserted += 1
            slug = a.get("subcategory_key", "?")
            conf = a.get("confidence", 0)
            print(f"  INSERT [{slug} {conf:.2f}] {a.get('title', '')[:55]}")

        session.commit()

    print(f"\n완료: 삽입 {inserted}개 / 중복 스킵 {skipped}개")
    if inserted > 0:
        print("\n다음 단계: 요약·임베딩 생성이 필요하면 아래 명령을 실행하세요.")
        print("  python scripts/run_ai_pipeline.py")


if __name__ == "__main__":
    main()
