#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""summaries_korean.json + articles_dump_korean_111.categorized.json 정적 분석.

DB 접속 없이 두 JSON 파일만 읽는다.
 - articles_dump_korean_111.categorized.json : 기사 정보(본문 paragraphs + 카테고리)
 - summaries_korean.json                     : 기사별 문단 요약 (id 1:1 매핑)

분석 목표 (사용자 요청):
  1) 카테고리별 기사 개수
  2) 원본 문단이 너무 짧은데 요약된(이상하게 부풀려진) 문단 탐지

사용법:
    cd backend
    python scripts/analyze_korean_json.py
"""
from __future__ import annotations

import collections
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
ART_PATH = BASE / "articles_dump_korean_111.categorized.json"
SUM_PATH = BASE / "summaries_korean.json"

# 원본 문단을 "너무 짧다"고 볼 기준 (글자 수)
SHORT_ORIG = 25


def h(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def main() -> None:
    arts = json.loads(ART_PATH.read_text(encoding="utf-8"))
    sums = json.loads(SUM_PATH.read_text(encoding="utf-8"))
    art_by_id = {a["id"]: a for a in arts}

    # ---------------- 0. 매핑 정합성 ----------------
    h("0. 파일 현황 & 1:1 매핑")
    aids, sids = {a["id"] for a in arts}, {s["id"] for s in sums}
    print(f"기사: {len(arts)}건 | 요약: {len(sums)}건 | 매칭: {len(aids & sids)}건")
    if aids - sids:
        print(f"  요약 없는 기사: {len(aids - sids)}건")
    if sids - aids:
        print(f"  기사 없는 요약: {len(sids - aids)}건")

    # ---------------- 1. 카테고리별 개수 ----------------
    h("1. 카테고리별 기사 개수")
    print("[category_group (대분류)]")
    for k, v in collections.Counter(a.get("category_group") for a in arts).most_common():
        print(f"  {str(k):<10}: {v:>3}건")

    print("\n[category_label_ko (소분류)]")
    for k, v in collections.Counter(a.get("category_label_ko") for a in arts).most_common():
        print(f"  {str(k):<16}: {v:>3}건")

    print("\n[category (slug)]")
    for k, v in collections.Counter(a.get("category") for a in arts).most_common():
        print(f"  {str(k):<22}: {v:>3}건")

    # ---------------- 2. 원본 문단이 너무 짧은데 요약된 케이스 ----------------
    h(f"2. 원본 문단이 짧은데(≤{SHORT_ORIG}자) 요약된 문단 탐지")
    print("기준: 원본 문단 길이 ≤ 25자 → 소제목/한줄 문장. 이런 문단은")
    print("      요약이 원본보다 길거나(부풀림), 내용을 지어내기 쉬움.\n")

    flagged = []  # (title, idx, orig, summ, ratio)
    total_pairs = 0
    short_orig_total = 0

    for s in sums:
        a = art_by_id.get(s["id"])
        if not a:
            continue
        paras = a.get("paragraphs") or []
        title = a.get("title", "")[:55]
        for p in s.get("paragraph_summaries") or []:
            idx = p.get("paragraph_index")
            summ = (p.get("summary") or "").strip()
            if idx is None or idx >= len(paras):
                continue
            orig = (paras[idx] or "").strip()
            total_pairs += 1
            if len(orig) <= SHORT_ORIG:
                short_orig_total += 1
                ratio = (len(summ) / len(orig)) if orig else 0
                # 원본이 짧은데 요약이 원본보다 길면 부풀림 의심
                if len(summ) >= len(orig):
                    flagged.append((title, idx, orig, summ, ratio))

    print(f"전체 (원본↔요약) 문단 쌍: {total_pairs}개")
    print(f"원본 ≤{SHORT_ORIG}자 문단: {short_orig_total}개")
    print(f"그 중 '요약이 원본보다 김(부풀림 의심)': {len(flagged)}개\n")

    # 부풀림 비율 큰 순으로 정렬
    flagged.sort(key=lambda x: x[4], reverse=True)
    for title, idx, orig, summ, ratio in flagged:
        print(f"[{title}] 문단{idx}  (원본{len(orig)}자→요약{len(summ)}자, x{ratio:.1f})")
        print(f"   원본: {orig}")
        print(f"   요약: {summ}")
        print()


if __name__ == "__main__":
    main()
