"""
전체 기사에 대해 AI 요약 → 임베딩 벡터 생성을 순차 실행하는 파이프라인.

- Phase 1: one_line_summary가 없는 기사 전체 요약 생성
- Phase 2: 임베딩이 없는 기사 전체 임베딩 생성

중단 후 재실행해도 이미 처리된 기사는 자동으로 건너뜁니다.

실행: python scripts/run_ai_pipeline.py (backend/ 디렉토리에서)
"""

import re
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import exists
from app.core.database import SessionLocal
from app.models.article import Article
from app.models.category import Category, Subcategory  # noqa: F401
from app.models.keyword import ArticleKeyword
from app.services.summarizer import summarize_article
from app.services.embedder import embed_article


def _is_quota_error(e: Exception) -> bool:
    return "RESOURCE_EXHAUSTED" in str(e)


def _is_unavailable_error(e: Exception) -> bool:
    return "UNAVAILABLE" in str(e)


# 순환할 요약 모델 풀 (앞에서부터 순서대로 사용, quota 소진 시 다음으로 전환)
SUMMARIZE_MODELS = [
    "models/gemini-3.5-flash",
    "models/gemini-2.5-flash",
    "models/gemini-2.0-flash",
    # "models/gemini-3.1-flash-lite",
    # "models/gemini-2.5-flash-lite",
]


# Gemini free tier 기준 딜레이 (RPM 대응)
SUMMARIZE_DELAY = 4.0
EMBED_DELAY = 0.5


def _parse_retry_delay(exc: Exception) -> int:
    """429 응답에서 Gemini가 알려주는 retryDelay를 파싱해 정수(초)로 반환."""
    match = re.search(r"retryDelay.*?(\d+)s", str(exc))
    if match:
        return int(match.group(1)) + 5  # 버퍼 5초 추가
    return 30


def phase1_summarize(db):
    articles = (
        db.query(Article)
        .filter(Article.one_line_summary == None)  # noqa: E711
        .filter(Article.original_content != None)
        .order_by(Article.published_at.desc())
        .all()
    )

    if not articles:
        print("  요약할 기사 없음. (모두 처리됨)\n")
        return

    print(f"  대상 기사 {len(articles)}개\n" + "-" * 60)
    success = skipped = 0
    model_idx = 0

    for i, article in enumerate(articles, 1):
        print(f"  [{i}/{len(articles)}] {article.title[:75]}")
        result = None

        while model_idx < len(SUMMARIZE_MODELS):
            current_model = SUMMARIZE_MODELS[model_idx]
            try:
                result = summarize_article(article.id, db, model=current_model)
                break  # 성공 시 다음 기사로
            except Exception as e:
                if _is_quota_error(e):
                    model_idx += 1
                    if model_idx < len(SUMMARIZE_MODELS):
                        print(
                            f"    [{current_model}] quota 소진 → {SUMMARIZE_MODELS[model_idx]}으로 전환"
                        )
                    else:
                        print(
                            f"    [{current_model}] quota 소진 — 모든 모델 소진. 오늘 처리 중단"
                        )
                elif _is_unavailable_error(e):
                    print(f"    [503] 30초 대기 후 재시도 [{current_model}]")
                    time.sleep(30)
                    # 같은 model_idx로 while 재진입
                else:
                    print(f"    실패 (skip): {e}")
                    result = None
                    break

        if model_idx >= len(SUMMARIZE_MODELS):
            print(f"\n  모든 모델의 일일 quota 소진. 내일 재실행하세요.")
            break

        if result is None:
            print("    실패: 파싱 오류 또는 본문 없음 (skip)")
            skipped += 1
        else:
            print(f"    완료 [{SUMMARIZE_MODELS[model_idx]}]")
            success += 1

        time.sleep(SUMMARIZE_DELAY)

    print(f"\n  Phase 1 결과: 성공 {success} / 실패 {skipped} / 전체 {len(articles)}\n")


def phase2_embed(db):
    articles = (
        db.query(Article)
        .filter(Article.one_line_summary != None)
        .filter(~exists().where(ArticleKeyword.article_id == Article.id))
        .order_by(Article.published_at.desc())
        .all()
    )

    if not articles:
        print("  임베딩할 기사 없음. (모두 처리됨)\n")
        return

    print(f"  대상 기사 {len(articles)}개\n" + "-" * 60)
    success = skipped = 0

    for i, article in enumerate(articles, 1):
        print(f"  [{i}/{len(articles)}] {article.title[:75]}")
        try:
            embed_article(article.id, article.title, article.paragraph_summary, db)
            count = (
                db.query(ArticleKeyword)
                .filter(ArticleKeyword.article_id == article.id)
                .count()
            )
            print(f"    완료: 벡터 {count}개")
            success += 1
        except Exception as e:
            if not _is_quota_error(e):
                print(f"    실패 (skip): {e}")
                skipped += 1
                time.sleep(EMBED_DELAY)
                continue
            wait = _parse_retry_delay(e)
            print(f"    [Rate limit] {wait}초 대기 후 재시도")
            time.sleep(wait)
            try:
                embed_article(article.id, article.title, article.paragraph_summary, db)
                success += 1
            except Exception as e2:
                print(f"    실패 (skip): {e2}")
                skipped += 1
        time.sleep(EMBED_DELAY)

    print(f"\n  Phase 2 결과: 성공 {success} / 실패 {skipped} / 전체 {len(articles)}\n")


def main():
    db = SessionLocal()
    try:
        print("=" * 60)
        print("[Phase 1] AI 요약 생성")
        print("=" * 60)
        phase1_summarize(db)

        print("=" * 60)
        print("[Phase 2] 임베딩 벡터 생성")
        print("=" * 60)
        phase2_embed(db)

        print("파이프라인 완료!")

    finally:
        db.close()


if __name__ == "__main__":
    main()
