"""confidence = 0.0 (no_match) 기사들의 카테고리/서브카테고리 분포 확인."""
from __future__ import annotations

import app.models.article   # noqa: F401
import app.models.category  # noqa: F401
import app.models.keyword   # noqa: F401
from sqlalchemy import func
from app.core.database import SessionLocal
from app.models.article import Article
from app.models.category import Category, Subcategory


def main() -> None:
    with SessionLocal() as s:
        total_articles = s.query(func.count(Article.id)).scalar()
        no_match_total = (
            s.query(func.count(Article.id))
            .filter(Article.confidence == 0.0)
            .scalar()
        )
        print(f"전체 기사 수: {total_articles}")
        print(f"no_match (confidence=0.0) 기사 수: {no_match_total}")
        print()

        # 1) 대분류 분포
        print("== 대분류(Category) 분포 ==")
        cat_rows = (
            s.query(Category.key, Category.label, func.count(Article.id))
            .join(Article, Article.category_id == Category.id)
            .filter(Article.confidence == 0.0)
            .group_by(Category.key, Category.label)
            .order_by(func.count(Article.id).desc())
            .all()
        )
        for key, label, cnt in cat_rows:
            pct = (cnt / no_match_total * 100) if no_match_total else 0
            print(f"  {key:<6} ({label}): {cnt:>3} 건 ({pct:5.1f}%)")
        print()

        # 2) 소분류 분포 (대분류 묶음)
        print("== 소분류(Subcategory) 분포 ==")
        sub_rows = (
            s.query(
                Category.key,
                Subcategory.key,
                Subcategory.label,
                func.count(Article.id),
            )
            .join(Subcategory, Subcategory.category_id == Category.id)
            .join(Article, Article.subcategory_id == Subcategory.id)
            .filter(Article.confidence == 0.0)
            .group_by(Category.key, Subcategory.key, Subcategory.label)
            .order_by(Category.key, func.count(Article.id).desc())
            .all()
        )
        current_cat = None
        for cat_key, sub_key, sub_label, cnt in sub_rows:
            if cat_key != current_cat:
                print(f"\n  [{cat_key}]")
                current_cat = cat_key
            pct = (cnt / no_match_total * 100) if no_match_total else 0
            print(f"    {sub_key:<20} ({sub_label}): {cnt:>3} 건 ({pct:5.1f}%)")


if __name__ == "__main__":
    main()
