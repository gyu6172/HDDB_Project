"""문단 11~13개짜리 기사들의 paragraph_summary 내용 살펴보기."""
from __future__ import annotations

import json
from sqlalchemy import text
from app.core.database import SessionLocal


def main() -> None:
    with SessionLocal() as s:
        q = text(
            """
            SELECT a.id, a.title, a.source, a.source_lang,
                   LENGTH(a.original_content)              AS orig_len,
                   jsonb_array_length(a.paragraph_summary::jsonb) AS plen,
                   a.one_line_summary,
                   a.card_summary,
                   a.paragraph_summary,
                   a.confidence,
                   c.key AS cat_key
            FROM articles a
            JOIN categories c ON c.id = a.category_id
            WHERE a.confidence IS NOT NULL
              AND a.confidence <> 0
              AND jsonb_array_length(a.paragraph_summary::jsonb) >= 5
            ORDER BY plen
            """
        )
        rows = s.execute(q).all()
        print(f"검사 대상: {len(rows)} 건\n")

        for row in rows:
            (
                aid, title, source, lang, orig_len, plen,
                one_line, card, paragraphs, conf, cat_key,
            ) = row
            print("=" * 80)
            print(f"id          : {aid}")
            print(f"title       : {title}")
            print(f"source      : {source}  lang={lang}  cat={cat_key}  conf={conf:.3f}")
            print(f"original len: {orig_len}")
            print(f"paragraphs  : {plen}")
            print(f"one_line    : {one_line}")
            print(f"card        : {(card or '')[:200]}")
            print()
            print("-- paragraph_summary items --")
            for i, item in enumerate(paragraphs):
                idx = item.get("paragraph_index")
                orig = item.get("original_text") or ""
                summ = item.get("summary") or ""
                print(
                    f"[{i}] idx={idx}  "
                    f"orig_len={len(orig)}  summ_len={len(summ)}  "
                    f"identical={orig.strip() == summ.strip()}"
                )
                print(f"     orig: {orig[:140]}{'...' if len(orig) > 140 else ''}")
                print(f"     summ: {summ[:140]}{'...' if len(summ) > 140 else ''}")
            print()


if __name__ == "__main__":
    main()
