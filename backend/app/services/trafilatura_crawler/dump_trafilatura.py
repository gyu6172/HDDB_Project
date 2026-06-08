"""DB의 original_url로 trafilatura 전문 수집 후 덤프 JSON 저장.

기존 dump_articles.py와 동일한 출력 구조에 original_url 필드 추가.
paragraph_summary IS NULL인 기사 중 trafilatura 효과가 큰 소스 위주로 샘플링.

실행:
  python summarize_offline/dump_trafilatura.py --limit 10 --out summarize_offline/articles_dump_trafilatura.json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import html as html_lib
sys.path.insert(0, ".")
# 스크립트 자신의 디렉터리를 path 에 추가해 clean_paragraphs 를 import 가능하게 한다.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import trafilatura
from app.core.database import SessionLocal
from app.models.article import Article
from app.models.category import Category, Subcategory  # noqa: F401
from sqlalchemy import text

from clean_paragraphs import clean_paragraphs


def _split_paragraphs(text: str) -> list[str]:
    """summarizer.py와 동일한 단락 분리 로직."""
    paras = [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]
    if len(paras) <= 1:
        paras = [p.strip() for p in re.split(r"\n", text) if p.strip()]
    return paras


def _fetch(url: str, timeout: int = 20) -> tuple[str, str]:
    """trafilatura로 원문 수집. (content, status) 반환."""
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return "", "no_response"
        extracted = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=False,
            no_fallback=False,
        )
        if extracted and len(extracted.strip()) > 50:
            return extracted.strip(), "ok"
        return "", "empty"
    except Exception as e:
        return "", f"error:{e}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--out", default="summarize_offline/articles_dump_trafilatura.json")
    ap.add_argument("--delay", type=float, default=1.5, help="요청 간 딜레이(초)")
    ap.add_argument("--no-clean", action="store_true",
                    help="보일러플레이트 정제를 끄고 원문 그대로 저장")
    args = ap.parse_args()

    db = SessionLocal()
    rows = db.execute(text("""
        SELECT id, title, source_lang, source, original_url,
               LENGTH(COALESCE(original_content, '')) AS old_len
        FROM articles
        WHERE original_url IS NOT NULL
        ORDER BY RANDOM()
        LIMIT :lim
    """), {"lim": args.limit}).fetchall()
    db.close()

    clean = not args.no_clean
    print(f"대상 {len(rows)}건 수집 시작... (정제 {'ON' if clean else 'OFF'})")
    print(f"{'SOURCE':35s} {'OLD':>6} {'NEW':>7} {'DROP':>5}  STATUS")
    print("-" * 72)

    results = []
    total_dropped = 0
    for r in rows:
        aid, title, lang, source, url, old_len = r
        content, status = _fetch(url)

        paragraphs = _split_paragraphs(content) if content else []
        # 수집 직후 보일러플레이트(날짜/출처/광고/인용 등) 정제
        dropped = 0
        if clean and paragraphs:
            paragraphs, removed = clean_paragraphs(title or "", paragraphs)
            dropped = len(removed)
            total_dropped += dropped
        # 정제 후 본문 길이로 갱신
        new_len = sum(len(p) for p in paragraphs)

        ratio_str = f"+{new_len/max(old_len,1):.1f}x" if status == "ok" else status
        print(f"{source[:35]:35s} {old_len:6d} {new_len:7d} {dropped:5d}  {ratio_str}")

        results.append({
            "id": aid,
            "title": title,
            "source_lang": lang,
            "source": source,
            "original_url": url,
            "old_content_len": old_len,
            "new_content_len": new_len,
            "status": status,
            "paragraphs": paragraphs,
        })

        time.sleep(args.delay)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    ok = sum(1 for r in results if r["status"] == "ok")
    print(f"\n완료: {ok}/{len(results)}건 성공, 정제로 {total_dropped}개 문단 제거 → {args.out}")


if __name__ == "__main__":
    main()
