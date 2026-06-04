"""
article_keywords 재생성 스크립트.

- 이미 임베딩된 기사는 기본적으로 건너뜀 (재실행 안전)
- --force 옵션 시 기존 키워드 삭제 후 전체 재생성
- RPM 초과 시 30초 대기 후 재시도
- RPD 초과 시 중단 → 내일 재실행하면 이어서 진행

실행:
  python scripts/reembed_articles.py            # 미완료 기사만
  python scripts/reembed_articles.py --force    # 전체 재생성
"""
import sys
import os
import argparse
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.article import Article
from app.models.category import *
from app.models.keyword import ArticleKeyword
from app.services.embedder import embed_article


def main(force: bool) -> None:
    db = SessionLocal()
    try:
        articles = db.query(Article).order_by(Article.created_at).all()

        # 이미 임베딩된 article_id 목록
        embedded_ids = set(
            r[0] for r in db.query(ArticleKeyword.article_id).distinct().all()
        )

        if force:
            print(f"[--force] 기존 article_keywords 전체 삭제 중...")
            db.query(ArticleKeyword).delete()
            db.commit()
            embedded_ids = set()
            print(f"삭제 완료\n")

        targets = [a for a in articles if a.id not in embedded_ids]
        total = len(articles)
        already_done = total - len(targets)

        print(f"전체: {total}개 | 기완료: {already_done}개 | 대상: {len(targets)}개\n")

        success = 0
        skipped = 0

        for i, article in enumerate(targets, 1):
            para_count = len([
                p for p in (article.paragraph_summary or [])
                if p.get("summary")
            ])
            call_count = 1 + para_count  # title + paragraphs

            print(f"[{i:3d}/{len(targets)}] {article.title[:60]}")
            print(f"         API 호출 예정: {call_count}회 (title 1 + 문단 {para_count}개)")

            retry = 0
            while True:
                try:
                    embed_article(
                        article_id=article.id,
                        title=article.title,
                        paragraph_summary=article.paragraph_summary,
                        db=db,
                    )
                    success += 1
                    print(f"         완료")
                    break

                except Exception as e:
                    err = str(e)
                    if "RESOURCE_EXHAUSTED" not in err and "quota" not in err.lower():
                        print(f"         [SKIP] 에러: {err[:80]}")
                        skipped += 1
                        break

                    # RPM vs RPD 구분: 에러 메시지에 "minute" 포함 여부
                    is_rpm = "minute" in err.lower() or "per_minute" in err.lower()

                    if is_rpm:
                        retry += 1
                        if retry > 5:
                            print(f"         [SKIP] RPM 재시도 5회 초과, 건너뜀")
                            skipped += 1
                            break
                        print(f"         [RPM 초과] 30초 대기 후 재시도... ({retry}/5)")
                        time.sleep(30)
                    else:
                        # RPD 초과
                        print(f"\n[RPD 초과] 일일 API 한도에 도달했습니다.")
                        print(f"완료: {success}개 / 남은 대상: {len(targets) - i}개")
                        print(f"내일 다시 실행하면 이어서 진행됩니다.")
                        return

    finally:
        db.close()

    print(f"\n=== 완료 ===")
    print(f"성공: {success}개 | 스킵(에러): {skipped}개 | 기완료(건너뜀): {already_done}개")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="기존 키워드 삭제 후 전체 재생성")
    args = ap.parse_args()
    main(force=args.force)
