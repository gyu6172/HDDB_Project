"""confidence != 0 이고 paragraph_summary 길이가 1인 기사들의 카테고리 분포."""
from __future__ import annotations

from sqlalchemy import text
from app.core.database import SessionLocal


def main() -> None:
    with SessionLocal() as s:
        total_q = text(
            """
            SELECT COUNT(*)
            FROM articles
            WHERE confidence IS NOT NULL
              AND confidence <> 0
              AND jsonb_array_length(paragraph_summary::jsonb) = 1
            """
        )
        matched_total = s.execute(total_q).scalar() or 0
        print(
            "조건 (confidence != 0 AND paragraph_summary 길이 == 1) "
            f"만족 기사 수: {matched_total}"
        )
        print()
        if matched_total == 0:
            return

        cat_q = text(
            """
            SELECT c.key,
                   c.label,
                   COUNT(a.id)        AS cnt,
                   AVG(a.confidence)  AS avg_conf
            FROM articles a
            JOIN categories c ON c.id = a.category_id
            WHERE a.confidence IS NOT NULL
              AND a.confidence <> 0
              AND jsonb_array_length(a.paragraph_summary::jsonb) = 1
            GROUP BY c.key, c.label
            ORDER BY cnt DESC
            """
        )
        print("== 대분류(Category) 분포 ==")
        for key, label, cnt, avg in s.execute(cat_q).all():
            pct = cnt / matched_total * 100
            print(
                f"  {key:<6} ({label}): {cnt:>4} 건 "
                f"({pct:5.1f}%)  avg_conf={avg:.3f}"
            )
        print()

        sub_q = text(
            """
            SELECT c.key       AS cat_key,
                   sc.key      AS sub_key,
                   sc.label    AS sub_label,
                   COUNT(a.id) AS cnt,
                   AVG(a.confidence) AS avg_conf
            FROM articles a
            JOIN categories    c  ON c.id  = a.category_id
            JOIN subcategories sc ON sc.id = a.subcategory_id
            WHERE a.confidence IS NOT NULL
              AND a.confidence <> 0
              AND jsonb_array_length(a.paragraph_summary::jsonb) = 1
            GROUP BY c.key, sc.key, sc.label
            ORDER BY c.key, cnt DESC
            """
        )
        print("== 소분류(Subcategory) 분포 ==")
        current_cat = None
        for cat_key, sub_key, sub_label, cnt, avg in s.execute(sub_q).all():
            if cat_key != current_cat:
                print(f"\n  [{cat_key}]")
                current_cat = cat_key
            pct = cnt / matched_total * 100
            print(
                f"    {sub_key:<22} ({sub_label}): {cnt:>4} 건 "
                f"({pct:5.1f}%)  avg_conf={avg:.3f}"
            )


if __name__ == "__main__":
    main()
