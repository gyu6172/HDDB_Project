"""
요약이 완료된 기사에 대해 임베딩 벡터를 생성하는 테스트 스크립트.
article_keywords에 row가 없는 기사만 대상으로 합니다.

실행: python test_embed.py (backend/ 디렉토리에서)
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import not_, exists
from app.core.database import SessionLocal
from app.models.article import Article
from app.models.category import Category, Subcategory  # noqa: F401
from app.models.keyword import ArticleKeyword
from app.services.embedder import embed_article


def main():
    db = SessionLocal()
    try:
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
            print("임베딩할 기사가 없어요. (요약 완료 + 임베딩 미완료 기사 없음)")
            return

        print(f"임베딩 대상 기사 {len(articles)}개\n" + "=" * 60)

        success = 0
        for i, article in enumerate(articles, 1):
            print(f"\n[{i}/{len(articles)}] {article.title[:80]}")
            try:
                embed_article(article.id, article.title, article.paragraph_summary, db)
                count = db.query(ArticleKeyword).filter(
                    ArticleKeyword.article_id == article.id
                ).count()
                print(f"  완료: 벡터 {count}개 생성")
                success += 1
            except Exception as e:
                print(f"  실패: {e}")

        print(f"\n" + "=" * 60)
        print(f"완료: {success}/{len(articles)}개 성공")

    finally:
        db.close()


if __name__ == "__main__":
    main()
