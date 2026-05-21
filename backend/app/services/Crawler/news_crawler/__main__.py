"""CLI 진입점.

사전 준비:
    1) `pip install -r requirements.txt`
    2) Ollama 설치 후 `ollama serve` 실행 (https://ollama.com/download)
       및 사용 모델 pull: `ollama pull qwen2.5:3b`
    3) (선택) .env 또는 환경변수:
       OLLAMA_HOST=http://localhost:11434
       OLLAMA_MODEL=qwen2.5:3b
       OLLAMA_TIMEOUT=120
       MAX_ARTICLES_TOTAL=50           # 한 번 crawl 시 저장할 최대 기사 수
       MAX_ENTRIES_PER_SOURCE=50       # 한 소스에서 후보로 가져올 최대 RSS 엔트리 수

사용 예:
    python -m news_crawler init                       # 테이블 + 소스/카테고리 시드
    python -m news_crawler sync-sources               # YAML/카테고리 변경 후 DB 동기화
    python -m news_crawler crawl                      # 자연 관련 기사만 분류해 저장
    python -m news_crawler crawl --lang ko            # ko 소스만
    python -m news_crawler list-sources
    python -m news_crawler show --limit 10                       # 최근 기사
    python -m news_crawler show --group sea --limit 10           # 바다 카테고리만
    python -m news_crawler show --category marine_life           # 해양생물만
    python -m news_crawler export news.txt --limit 50            # 파일로 저장
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from sqlalchemy import func, select

from .classifier import OllamaClassifier, OllamaUnavailable
from .crawler import crawl_all
from .db import SessionLocal, init_db
from .models import Article, Source
from .seed import sync_categories, sync_sources
from .viewer import export_articles_to_file, fetch_articles, render_articles


def _cmd_init(_: argparse.Namespace) -> int:
    init_db()
    added, updated = sync_sources()
    cat_added = sync_categories()
    print(
        f"DB ready. sources: +{added} added, {updated} updated. "
        f"categories: +{cat_added} added."
    )
    return 0


def _cmd_sync(_: argparse.Namespace) -> int:
    added, updated = sync_sources()
    cat_added = sync_categories()
    print(f"sources: +{added} added, {updated} updated. categories: +{cat_added} added.")
    return 0


def _cmd_crawl(args: argparse.Namespace) -> int:
    init_db()  # DB가 비어 있어도 바로 동작하도록 보장
    try:
        classifier = OllamaClassifier()
    except OllamaUnavailable as exc:
        print(f"[ERROR] {exc}")
        return 2
    results = crawl_all(language=args.lang, classifier=classifier)
    total_new = sum(r.inserted for r in results)
    total_prefiltered = sum(r.prefiltered for r in results)
    for r in results:
        if r.error:
            flag = f"ERROR: {r.error}"
        else:
            flag = f"new={r.inserted} skip={r.skipped} prefiltered={r.prefiltered}"
        print(f"[{r.source}] fetched={r.fetched} {flag}")
    print(
        f"\nTotal new articles: {total_new}  "
        f"(prefiltered without LLM call: {total_prefiltered}, "
        f"Ollama calls used: {classifier.call_count}, model: {classifier.model_name})"
    )
    return 0


def _cmd_list_sources(_: argparse.Namespace) -> int:
    with SessionLocal() as session:
        rows = session.scalars(select(Source).order_by(Source.language, Source.name)).all()
        if not rows:
            print("(no sources registered)")
            return 0
        for s in rows:
            print(f"{s.id:>3}  [{s.language}] {s.name}  -  {s.url}  {'(off)' if not s.active else ''}")
    return 0


def _cmd_show(args: argparse.Namespace) -> int:
    articles = fetch_articles(
        language=args.lang,
        source=args.source,
        category=args.category,
        group=args.group,
        limit=args.limit,
    )
    print(render_articles(articles, full=args.full))
    return 0


def _cmd_export(args: argparse.Namespace) -> int:
    articles = fetch_articles(
        language=args.lang,
        source=args.source,
        category=args.category,
        group=args.group,
        limit=args.limit,
    )
    text = render_articles(articles, full=args.full)
    path = export_articles_to_file(text, Path(args.path))
    print(f"saved {len(articles)} articles -> {path.resolve()}")
    return 0


def _cmd_stats(_: argparse.Namespace) -> int:
    with SessionLocal() as session:
        total = session.scalar(select(func.count()).select_from(Article)) or 0
        ko = session.scalar(
            select(func.count()).select_from(Article).where(Article.language == "ko")
        ) or 0
        en = session.scalar(
            select(func.count()).select_from(Article).where(Article.language == "en")
        ) or 0
        print(f"articles: total={total}  ko={ko}  en={en}")
    return 0


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(prog="news_crawler")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="create tables and seed sources").set_defaults(func=_cmd_init)
    sub.add_parser("sync-sources", help="sync sources.yaml -> DB").set_defaults(func=_cmd_sync)

    crawl_p = sub.add_parser("crawl", help="fetch latest articles from active sources")
    crawl_p.add_argument("--lang", choices=["ko", "en"], help="filter by language")
    crawl_p.set_defaults(func=_cmd_crawl)

    sub.add_parser("list-sources", help="print registered sources").set_defaults(func=_cmd_list_sources)
    sub.add_parser("stats", help="print article counts").set_defaults(func=_cmd_stats)

    def _add_view_filters(p: argparse.ArgumentParser) -> None:
        p.add_argument("--lang", choices=["ko", "en"], help="filter by language")
        p.add_argument("--source", help="filter by source name (substring match)")
        p.add_argument(
            "--category",
            help="filter by category slug (예: bird, marine_life, disaster ...)",
        )
        p.add_argument(
            "--group", choices=["sky", "land", "sea"], help="filter by category group"
        )
        p.add_argument("--limit", type=int, default=20, help="max articles (default 20)")
        p.add_argument("--full", action="store_true", help="print full body instead of preview")

    show_p = sub.add_parser("show", help="print saved articles as readable text")
    _add_view_filters(show_p)
    show_p.set_defaults(func=_cmd_show)

    export_p = sub.add_parser("export", help="save articles to a .txt file")
    export_p.add_argument("path", help="output file path (e.g. news.txt)")
    _add_view_filters(export_p)
    export_p.set_defaults(func=_cmd_export)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
