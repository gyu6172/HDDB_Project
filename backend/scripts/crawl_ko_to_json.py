#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
한국어 기사 크롤링 -> JSON 출력 스크립트 (DB 쓰기 없음).

RSS 수집 -> trafilatura 전문 추출 -> Gemini 분류 -> JSON 저장

사용법:
    cd backend
    python scripts/crawl_ko_to_json.py
    python scripts/crawl_ko_to_json.py --target 4 --delay 2.0
    python scripts/crawl_ko_to_json.py --out scripts/output/my_articles.json

옵션:
    --target  서브카테고리당 목표 기사 수 (기본값: 3)
    --delay   trafilatura 요청 간 딜레이(초) (기본값: 1.5)
    --out     출력 JSON 경로
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from time import mktime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import feedparser
import trafilatura
from google import genai
from sqlalchemy import select

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.category import Subcategory
from app.services.Crawler.news_crawler.classifier import CATEGORY_DEFS
from app.services.Crawler.news_crawler.classifier import passes_prefilter
from app.services.Crawler.news_crawler.text import strip_tags

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 한국어 소스 목록 (RSS 유효성 검증 완료)
# ---------------------------------------------------------------------------
KO_SOURCES = [
    ("경향신문 - 사회(환경/재난 포함)", "https://www.khan.co.kr/rss/rssdata/society_news.xml"),
    ("경향신문 - 과학", "https://www.khan.co.kr/rss/rssdata/science_news.xml"),
    ("연합뉴스 - 전체", "https://www.yna.co.kr/rss/news.xml"),
    ("오마이뉴스 - 전체", "https://rss.ohmynews.com/rss/ohmynews.xml"),
    ("한겨레21", "https://h21.hani.co.kr/rss"),
]

_GEMINI_MODEL = "models/gemini-2.0-flash"
_GEMINI_MIN_INTERVAL = 7.0  # free tier: 10 RPM → 6초 간격. 여유분 1초 추가
_last_gemini_call: float = 0.0


# ---------------------------------------------------------------------------
# Gemini 분류기
# ---------------------------------------------------------------------------
def _build_classify_prompt(title: str, content: str) -> str:
    catalog = "\n".join(
        f'- "{slug}" ({group}/{label_ko}): {desc}'
        for group, slug, label_ko, desc in CATEGORY_DEFS
    )
    return f"""당신은 뉴스 기사 분류기입니다. 아래 기사를 읽고, 자연 관련 카테고리 중 "가장 적합한" 단 한 개를
선택하고, 그 분류에 대한 확신도(confidence)를 0.000~1.000 사이 값으로 함께 매기세요.

[카테고리 목록]
{catalog}

[분류 규칙]
1. 자연(하늘/땅/바다)과 무관한 기사(정치, 경제, 연예, 스포츠, 일반 사회 등)이면
   {{"slug": null, "confidence": 0.0}} 을 반환하세요.
2. 자연 관련이면 가장 적합한 slug 하나만 반환하세요.
3. confidence 는 소수점 셋째 자리까지 표기 (예: 0.873).

[출력 형식 — JSON 만 출력, 다른 텍스트 없이]
{{"slug": "<slug_or_null>", "confidence": <float>}}

[기사 제목]
{title}

[기사 본문]
{content[:1500]}
"""


def _classify(client, title: str, content: str, retries: int = 3) -> tuple[str | None, float]:
    """Gemini로 기사 분류. (slug|None, confidence) 반환.

    free tier 10 RPM 제한을 지키기 위해 호출 사이에 최소 간격을 두고,
    429/503 응답 시 지수 백오프로 재시도한다.
    """
    global _last_gemini_call
    # 최소 호출 간격 유지
    elapsed = time.time() - _last_gemini_call
    if elapsed < _GEMINI_MIN_INTERVAL:
        time.sleep(_GEMINI_MIN_INTERVAL - elapsed)

    prompt = _build_classify_prompt(title, content)
    valid_slugs = {s for _, s, _, _ in CATEGORY_DEFS}

    for attempt in range(retries):
        try:
            _last_gemini_call = time.time()
            resp = client.models.generate_content(model=_GEMINI_MODEL, contents=prompt)
            m = re.search(r'\{.*?\}', resp.text.strip(), re.DOTALL)
            if not m:
                return None, 0.0
            data = json.loads(m.group(0))
            slug = data.get("slug") or None
            confidence = float(data.get("confidence", 0.0))
            if slug not in valid_slugs:
                slug = None
            return slug, max(0.0, min(1.0, confidence))
        except Exception as e:
            err_str = str(e)
            is_rate_limit = "429" in err_str or "RESOURCE_EXHAUSTED" in err_str
            is_unavailable = "503" in err_str or "UNAVAILABLE" in err_str
            if (is_rate_limit or is_unavailable) and attempt < retries - 1:
                # 429: 분당 한도 초과 → 60초 대기. 503: 일시적 과부하 → 15초 대기
                wait = 65 if is_rate_limit else 15 * (attempt + 1)
                logger.warning("Gemini 일시 오류 (%s), %d초 후 재시도 (%d/%d)...", err_str[:50], wait, attempt + 1, retries)
                time.sleep(wait)
                _last_gemini_call = time.time()
            else:
                logger.warning("Gemini 분류 실패: %s", err_str[:80])
                return None, 0.0
    return None, 0.0


# ---------------------------------------------------------------------------
# RSS / trafilatura 헬퍼
# ---------------------------------------------------------------------------
def _fetch_rss(url: str) -> list:
    feed = feedparser.parse(url, request_headers={"User-Agent": "Mozilla/5.0 (compatible; news-crawler/1.0)"})
    return feed.entries or []


def _fetch_full_content(url: str) -> str:
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return ""
        extracted = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=False,
            no_fallback=False,
        )
        return (extracted or "").strip()
    except Exception:
        return ""


def _parse_published(entry) -> str | None:
    for key in ("published_parsed", "updated_parsed", "created_parsed"):
        val = entry.get(key)
        if val:
            try:
                dt = datetime.fromtimestamp(mktime(val), tz=timezone.utc).replace(tzinfo=None)
                return dt.isoformat()
            except Exception:
                continue
    return None


def _pick_thumbnail(entry) -> str | None:
    for key in ("media_thumbnail", "media_content"):
        media = entry.get(key)
        if isinstance(media, list) and media:
            url = media[0].get("url")
            if url:
                return url
    for link in entry.get("links", []) or []:
        if link.get("rel") == "enclosure" and (link.get("type") or "").startswith("image"):
            href = link.get("href")
            if href:
                return href
    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description="한국어 기사 크롤링 → JSON (DB 쓰기 없음)")
    ap.add_argument("--target", type=int, default=3, help="서브카테고리당 목표 기사 수 (기본 3)")
    ap.add_argument("--delay", type=float, default=1.5, help="요청 간 딜레이 초 (기본 1.5)")
    ap.add_argument("--out", default="", help="출력 JSON 경로")
    args = ap.parse_args()

    today = datetime.now().strftime("%Y%m%d")
    out_path = (
        Path(args.out)
        if args.out
        else Path(__file__).parent / "output" / f"ko_articles_{today}.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # DB에서 subcategory 매핑 읽기 (read-only)
    with SessionLocal() as session:
        subcats = session.scalars(select(Subcategory)).all()
    if not subcats:
        logger.error("subcategories 테이블이 비어있습니다. DB init을 먼저 실행하세요.")
        sys.exit(1)

    sub_map = {sc.key: sc for sc in subcats}
    logger.info("서브카테고리 %d개 로드: %s", len(sub_map), list(sub_map.keys()))

    # Gemini 클라이언트
    client = genai.Client(api_key=settings.gemini_api_key)

    counts: dict[str, int] = {slug: 0 for slug in sub_map}
    articles: list[dict] = []
    seen_urls: set[str] = set()
    total_rss = total_prefiltered = total_gemini_calls = 0

    for source_name, rss_url in KO_SOURCES:
        if all(v >= args.target for v in counts.values()):
            logger.info("모든 카테고리 목표 달성, 수집 종료.")
            break

        logger.info("RSS 수집: %s", source_name)
        entries = _fetch_rss(rss_url)
        if not entries:
            logger.warning("  -> 기사 없음 (RSS 오류 또는 빈 피드)")
            continue

        total_rss += len(entries)
        logger.info("  -> %d개 항목 발견", len(entries))

        for entry in entries:
            if all(v >= args.target for v in counts.values()):
                break

            url = (entry.get("link") or "").strip()
            title = (entry.get("title") or "").strip()
            if not url or not title or url in seen_urls:
                continue
            seen_urls.add(url)

            # 1) trafilatura 전문 수집
            full_content = _fetch_full_content(url)
            if len(full_content) < 100:
                # trafilatura 실패 시 RSS summary로 fallback
                raw = entry.get("summary") or entry.get("description") or ""
                full_content = strip_tags(raw, replacement=" ").strip()

            if len(full_content) < 50:
                logger.debug("  -> 본문 너무 짧음, 스킵: %s", title[:40])
                time.sleep(0.3)
                continue

            # 2) 프리필터 (Gemini 호출 절약)
            if not passes_prefilter(title, full_content):
                total_prefiltered += 1
                logger.debug("  -> 프리필터 제외: %s", title[:40])
                time.sleep(0.3)
                continue

            # 3) Gemini 분류
            slug, confidence = _classify(client, title, full_content)
            total_gemini_calls += 1

            if slug is None or slug not in sub_map:
                logger.debug("  -> 자연 카테고리 아님: %s", title[:40])
                time.sleep(args.delay)
                continue

            if counts[slug] >= args.target:
                logger.debug("  -> '%s' 이미 목표치 도달, 스킵", slug)
                time.sleep(args.delay)
                continue

            sc = sub_map[slug]
            articles.append({
                "id": str(uuid.uuid4()),
                "title": title[:1024],
                "original_url": url,
                "original_content": full_content,
                "source_lang": "ko",
                "source": source_name,
                "published_at": _parse_published(entry),
                "thumbnail_url": _pick_thumbnail(entry),
                "category_id": sc.category_id,
                "subcategory_id": sc.id,
                "subcategory_key": slug,
                "confidence": confidence,
                "one_line_summary": None,
                "card_summary": None,
                "paragraph_summary": None,
            })
            counts[slug] += 1
            logger.info(
                "  [%s %.2f] (%d/%d) %s",
                slug, confidence, counts[slug], args.target, title[:50],
            )
            time.sleep(args.delay)

    # JSON 저장
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    # 결과 출력
    print("\n========== 수집 결과 ==========")
    print(f"RSS 처리: {total_rss}개  |  프리필터 제외: {total_prefiltered}개  |  Gemini 호출: {total_gemini_calls}개")
    print(f"최종 수집: {len(articles)}개  ->  {out_path}")
    print("\n[서브카테고리별 수집 현황]")
    for slug, cnt in sorted(counts.items()):
        filled = min(cnt, args.target)
        bar = "■" * filled + "□" * (args.target - filled)
        status = "완료" if cnt >= args.target else f"{cnt}/{args.target}"
        print(f"  {slug:20s} {bar}  {status}")

    unfilled = [s for s, c in counts.items() if c < args.target]
    if unfilled:
        print(f"\n[미달 카테고리] {unfilled}")
        print("  -> 해당 카테고리는 현재 RSS에 관련 기사가 부족합니다.")
        print("     --target 값을 낮추거나, 소스를 추가해보세요.")


if __name__ == "__main__":
    main()
