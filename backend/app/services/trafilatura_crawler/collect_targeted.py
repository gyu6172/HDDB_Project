"""부족 카테고리를 채우기 위한 타깃 수집기 (RSS 발견 → trafilatura 전문 → 정제 → 14b 분류).

RSS 피드는 '기사 URL 발견용'으로만 쓰고, 본문은 trafilatura 로 전문 수집한다.
(RSS 요약본은 짧으므로) 수집 → clean_paragraphs 정제 → HDDB 분류기(14b)로 분류 후,
부족 카테고리에 해당하고 아직 목표치(floor)에 못 미친 기사만 채택한다.

HDDB 코드/DB/sources.yaml 은 건드리지 않는다(분류기는 읽기 전용 import).

실행:
  python summarize_offline/collect_targeted.py            # floor=10 까지 수집
  python summarize_offline/collect_targeted.py --floor 12 --max-fetch 250
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys
import time
import uuid

import feedparser
import trafilatura

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)

from clean_paragraphs import clean_paragraphs
import classify_articles as ca  # load_classifier_module / DEFAULT_CLASSIFIER

# 부족 카테고리를 겨냥한 검증된 RSS 피드 (name, url, lang)
TARGET_FEEDS: list[tuple[str, str, str]] = [
    # 조류(bird) — 보충 수집 시 먼저 처리되도록 앞에 배치
    ("ScienceDaily - Birds", "https://www.sciencedaily.com/rss/plants_animals/birds.xml", "en"),
    ("The Guardian - Birds", "https://www.theguardian.com/environment/birds/rss", "en"),
    # 바다(marine_life / deep_sea / ocean_pollution)
    ("ScienceDaily - Marine Biology", "https://www.sciencedaily.com/rss/plants_animals/marine_biology.xml", "en"),
    ("ScienceDaily - Sea Life", "https://www.sciencedaily.com/rss/plants_animals/sea_life.xml", "en"),
    ("ScienceDaily - Fish", "https://www.sciencedaily.com/rss/plants_animals/fish.xml", "en"),
    ("ScienceDaily - Oceanography", "https://www.sciencedaily.com/rss/earth_climate/oceanography.xml", "en"),
    ("The Guardian - Oceans", "https://www.theguardian.com/environment/oceans/rss", "en"),
    ("The Guardian - Marine life", "https://www.theguardian.com/environment/marine-life/rss", "en"),
    # 오염(ocean_pollution / ground_pollution)
    ("ScienceDaily - Pollution", "https://www.sciencedaily.com/rss/earth_climate/pollution.xml", "en"),
    ("ScienceDaily - Environmental Issues", "https://www.sciencedaily.com/rss/earth_climate/environmental_issues.xml", "en"),
    ("The Guardian - Pollution", "https://www.theguardian.com/environment/pollution/rss", "en"),
    ("The Guardian - Plastic", "https://www.theguardian.com/environment/plastic/rss", "en"),
    # 동물(animal)
    ("ScienceDaily - Wild Animals", "https://www.sciencedaily.com/rss/plants_animals/wild_animals.xml", "en"),
]


def _split_paragraphs(text: str) -> list[str]:
    """dump_trafilatura 와 동일한 단락 분리."""
    paras = [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]
    if len(paras) <= 1:
        paras = [p.strip() for p in re.split(r"\n", text) if p.strip()]
    return paras


def _fetch(url: str) -> tuple[str, str]:
    """trafilatura 로 원문 수집. (content, status)."""
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return "", "no_response"
        extracted = trafilatura.extract(
            downloaded, include_comments=False, include_tables=False, no_fallback=False,
        )
        if extracted and len(extracted.strip()) > 50:
            return extracted.strip(), "ok"
        return "", "empty"
    except Exception as e:  # noqa: BLE001
        return "", f"error:{e}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--existing",
                    default=os.path.join(THIS_DIR, "articles_dump_trafilatura_100.categorized.json"),
                    help="기존 분류 결과(부족량 계산 + URL 중복 제거)")
    ap.add_argument("--out", default=os.path.join(THIS_DIR, "articles_dump_trafilatura_targeted.json"))
    ap.add_argument("--merged", default=os.path.join(THIS_DIR, "articles_dump_trafilatura_targeted_merged.json"))
    ap.add_argument("--floor", type=int, default=10, help="카테고리별 목표 최소 건수")
    ap.add_argument("--model", default="qwen2.5:14b-instruct-q4_K_M")
    ap.add_argument("--delay", type=float, default=1.2, help="trafilatura 요청 간 딜레이(초)")
    ap.add_argument("--max-per-feed", type=int, default=60)
    ap.add_argument("--max-fetch", type=int, default=300, help="전체 trafilatura 요청 상한(안전장치)")
    args = ap.parse_args()

    # 1) 기존 데이터로 부족량 + 중복 URL 계산
    with open(args.existing, encoding="utf-8") as f:
        existing = json.load(f)
    have = collections.Counter(a["category"] for a in existing if a.get("category"))
    seen_urls = {a.get("original_url") for a in existing if a.get("original_url")}

    clf_mod = ca.load_classifier_module(ca.DEFAULT_CLASSIFIER)
    meta = {slug: (group, label) for group, slug, label, _ in clf_mod.CATEGORY_DEFS}
    need = {cat: max(0, args.floor - have.get(cat, 0)) for cat in clf_mod.VALID_SLUGS}
    deficit = {c: n for c, n in need.items() if n > 0}

    print("[현재 보유]", dict(have))
    print("[목표 floor]", args.floor)
    print("[부족 카테고리]", deficit, "\n")
    if not deficit:
        print("이미 모든 카테고리가 목표를 충족합니다. 종료.")
        return

    classifier = clf_mod.OllamaClassifier(model=args.model)
    print(f"분류기 준비 (모델: {classifier.model_name})\n")

    kept: list[dict] = []
    kept_by_cat: collections.Counter[str] = collections.Counter()
    fetch_count = 0

    def remaining() -> dict[str, int]:
        return {c: deficit[c] - kept_by_cat[c] for c in deficit if deficit[c] - kept_by_cat[c] > 0}

    print(f"{'FEED':32s} {'CAT':16s} {'CONF':>6}  TITLE")
    print("-" * 92)

    for fname, furl, lang in TARGET_FEEDS:
        if not remaining():
            break
        parsed = feedparser.parse(furl, request_headers={"User-Agent": "news-crawler/1.0"})
        entries = parsed.entries[: args.max_per_feed]

        for entry in entries:
            if not remaining() or fetch_count >= args.max_fetch:
                break
            url = (entry.get("link") or "").strip()
            title = (entry.get("title") or "").strip()
            if not url or not title or url in seen_urls:
                continue
            seen_urls.add(url)

            # 비용 큰 trafilatura 호출 전, 제목+RSS요약으로 1차 사전필터
            rss_summary = entry.get("summary") or entry.get("description") or ""
            if not clf_mod.passes_prefilter(title, rss_summary):
                continue

            content, status = _fetch(url)
            fetch_count += 1
            time.sleep(args.delay)
            if status != "ok":
                continue

            paragraphs, _ = clean_paragraphs(title, _split_paragraphs(content))
            if not paragraphs:
                continue

            res = classifier.classify(title, "\n\n".join(paragraphs))
            slug = res.slug
            if not slug or slug not in deficit or kept_by_cat[slug] >= deficit[slug]:
                continue  # 부족 카테고리 아니거나 이미 채워짐 → 버림

            group, label = meta[slug]
            kept_by_cat[slug] += 1
            kept.append({
                "id": str(uuid.uuid4()),
                "title": title,
                "source_lang": lang,
                "source": fname,
                "original_url": url,
                "old_content_len": 0,
                "new_content_len": sum(len(p) for p in paragraphs),
                "status": status,
                "paragraphs": paragraphs,
                "category": slug,
                "category_group": group,
                "category_label_ko": label,
                "category_confidence": round(res.confidence, 3),
                "classify_note": "ok",
            })
            print(f"{fname[:32]:32s} {group+'/'+slug:16s} {res.confidence:6.3f}  {title[:42]}")

    # 2) 저장: 신규본 + 병합본
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(kept, f, ensure_ascii=False, indent=2)
    merged = existing + kept
    with open(args.merged, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 56)
    print(f"신규 채택: {len(kept)}건 / trafilatura 요청 {fetch_count}회 / LLM {classifier.call_count}회")
    print(f"저장(신규): {args.out}")
    print(f"저장(병합): {args.merged}\n")

    final = collections.Counter(a["category"] for a in merged if a.get("category"))
    print("[병합 후 카테고리 분포 / 목표 대비]")
    for _, slug, label, _ in clf_mod.CATEGORY_DEFS:
        v = final.get(slug, 0)
        mark = "OK" if v >= args.floor else f"부족 {args.floor - v}"
        print(f"  {slug:16s} {label:6s} {v:3d}  [{mark}]")


if __name__ == "__main__":
    main()
