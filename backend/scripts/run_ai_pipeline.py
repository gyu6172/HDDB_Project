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

try:
    from google.api_core.exceptions import ResourceExhausted
except ImportError:
    ResourceExhausted = Exception  # fallback

# Gemini free tier 기준 딜레이 (RPM 대응)
SUMMARIZE_DELAY = 4.0
EMBED_DELAY = 0.5
MAX_RETRIES = 3
DEFAULT_RETRY_WAIT = 30  # 초


def _parse_retry_delay(exc: Exception) -> int:
    """429 응답에서 Gemini가 알려주는 retryDelay를 파싱해 정수(초)로 반환."""
    match = re.search(r"retryDelay.*?(\d+)s", str(exc))
    if match:
        return int(match.group(1)) + 5  # 버퍼 5초 추가
    return DEFAULT_RETRY_WAIT


def call_with_retry(fn, *args, **kwargs):
    for attempt in range(MAX_RETRIES):
        try:
            return fn(*args, **kwargs)
        except ResourceExhausted as e:
            if attempt == MAX_RETRIES - 1:
                raise
            wait = _parse_retry_delay(e)
            print(f"    [Rate limit] {wait}초 대기 후 재시도 ({attempt + 1}/{MAX_RETRIES})")
            time.sleep(wait)


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
    for i, article in enumerate(articles, 1):
        print(f"  [{i}/{len(articles)}] {article.title[:75]}")
        try:
            result = call_with_retry(summarize_article, article.id, db)
            if result is None:
                print("    실패: 파싱 오류 또는 본문 없음 (skip)")
                skipped += 1
            else:
                print("    완료")
                success += 1
        except ResourceExhausted:
            print("    실패: 재시도 초과 (일일 quota 소진 가능성) — 내일 재실행하세요")
            skipped += 1
        except Exception as e:
            print(f"    실패 (skip): {e}")
            skipped += 1
        time.sleep(SUMMARIZE_DELAY)

    print(f"\n  Phase 1 결과: 성공 {success} / 실패 {skipped} / 전체 {len(articles)}\n")


def phase2_embed(db):
    articles = (
        db.query(Article)
        .filter(Article.one_line_summary != None)
        .filter(
            ~exists().where(ArticleKeyword.article_id == Article.id)
        )
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
            call_with_retry(
                embed_article,
                article.id, article.title, article.paragraph_summary, db,
            )
            count = db.query(ArticleKeyword).filter(
                ArticleKeyword.article_id == article.id
            ).count()
            print(f"    완료: 벡터 {count}개")
            success += 1
        except ResourceExhausted:
            print("    실패: 재시도 초과 (quota 소진) — 나중에 재실행하세요")
            skipped += 1
        except Exception as e:
            print(f"    실패 (skip): {e}")
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
