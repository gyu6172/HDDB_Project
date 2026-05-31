"""
Supabase DB에서 기사 5개를 가져와 요약을 생성하고 결과를 출력하는 테스트 스크립트.
summary가 없는 기사를 우선 선택합니다.

실행: python scripts/test_summarize.py (backend/ 디렉토리에서)
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import SessionLocal
from app.models.article import Article
from app.models.category import Category, Subcategory  # noqa: F401 — relationship 해소용
from app.services.summarizer import summarize_article

BATCH_SIZE = 5


def main():
    db = SessionLocal()
    try:
        articles = (
            db.query(Article)
            .filter(Article.one_line_summary == None)  # noqa: E711
            .filter(Article.original_content != None)
            .order_by(Article.published_at.desc())
            .limit(BATCH_SIZE)
            .all()
        )

        if not articles:
            print("요약 없는 기사가 없어요. 최신 기사로 테스트할게요.")
            articles = (
                db.query(Article)
                .filter(Article.original_content != None)
                .order_by(Article.published_at.desc())
                .limit(BATCH_SIZE)
                .all()
            )

        if not articles:
            print("DB에 기사가 없어요. 크롤러를 먼저 실행해 주세요.")
            return

        print(f"테스트 대상 기사 {len(articles)}개\n" + "=" * 60)

        for i, article in enumerate(articles, 1):
            print(f"\n[{i}/{len(articles)}] {article.title[:80]}")
            print(f"  ID: {article.id}")
            print(f"  기존 요약: {'있음' if article.one_line_summary else '없음'}")

            result = summarize_article(article.id, db)

            db.refresh(article)

            if result is not None:
                print(f"  한줄 요약: {article.one_line_summary}")
                print(f"  카드 요약: {article.card_summary}")
                print(f"  문단 수: {len(result)}개")
            else:
                print("  요약 생성 실패")

        print("\n" + "=" * 60)
        print("테스트 완료!")

    finally:
        db.close()


if __name__ == "__main__":
    main()
