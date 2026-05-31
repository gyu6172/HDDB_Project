"""confidence > 0.0 (분류기가 매칭한) 기사들의 카테고리/서브카테고리 분포 + 신뢰도 통계."""
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
        matched_total = (
            s.query(func.count(Article.id))
            .filter(Article.confidence > 0.0)
            .scalar()
        )
        print(f"전체 기사 수: {total_articles}")
        print(f"matched (confidence>0.0) 기사 수: {matched_total}")
        print()

        # 0) confidence 통계
        avg_c, min_c, max_c = (
            s.query(
                func.avg(Article.confidence),
                func.min(Article.confidence),
                func.max(Article.confidence),
            )
            .filter(Article.confidence > 0.0)
            .one()
        )
        print(f"confidence  avg={avg_c:.3f}  min={min_c:.3f}  max={max_c:.3f}")

        # confidence 구간 분포
        print("\n== confidence 구간 분포 ==")
        bins = [(0.0, 0.3), (0.3, 0.5), (0.5, 0.7), (0.7, 0.9), (0.9, 1.0001)]
        for lo, hi in bins:
            cnt = (
                s.query(func.count(Article.id))
                .filter(Article.confidence > lo, Article.confidence < hi)
                .scalar()
            )
            pct = (cnt / matched_total * 100) if matched_total else 0
            label = f"({lo:.1f}, {hi:.1f})" if hi < 1.0 else f"({lo:.1f}, 1.0]"
            print(f"  {label:<14}: {cnt:>3} 건 ({pct:5.1f}%)")
        print()

        # 1) 대분류 분포 (카운트 + 평균 confidence)
        print("== 대분류(Category) 분포 ==")
        cat_rows = (
            s.query(
                Category.key,
                Category.label,
                func.count(Article.id),
                func.avg(Article.confidence),
            )
            .join(Article, Article.category_id == Category.id)
            .filter(Article.confidence > 0.0)
            .group_by(Category.key, Category.label)
            .order_by(func.count(Article.id).desc())
            .all()
        )
        for key, label, cnt, avg in cat_rows:
            pct = (cnt / matched_total * 100) if matched_total else 0
            print(f"  {key:<6} ({label}): {cnt:>3} 건 ({pct:5.1f}%)  avg_conf={avg:.3f}")
        print()

        # 2) 소분류 분포 (대분류 묶음 + 평균 confidence)
        print("== 소분류(Subcategory) 분포 ==")
        sub_rows = (
            s.query(
                Category.key,
                Subcategory.key,
                Subcategory.label,
                func.count(Article.id),
                func.avg(Article.confidence),
            )
            .join(Subcategory, Subcategory.category_id == Category.id)
            .join(Article, Article.subcategory_id == Subcategory.id)
            .filter(Article.confidence > 0.0)
            .group_by(Category.key, Subcategory.key, Subcategory.label)
            .order_by(Category.key, func.count(Article.id).desc())
            .all()
        )
        current_cat = None
        for cat_key, sub_key, sub_label, cnt, avg in sub_rows:
            if cat_key != current_cat:
                print(f"\n  [{cat_key}]")
                current_cat = cat_key
            pct = (cnt / matched_total * 100) if matched_total else 0
            print(
                f"    {sub_key:<20} ({sub_label}): {cnt:>3} 건 "
                f"({pct:5.1f}%)  avg_conf={avg:.3f}"
            )


if __name__ == "__main__":
    main()
