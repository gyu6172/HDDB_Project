import logging
import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import not_, exists

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.article import Article
from app.models.keyword import ArticleKeyword
from app.services.crawler import ensure_categories_seeded, run_crawl
from app.services.summarizer import summarize_article
from app.services.embedder import embed_article

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

CRAWL_INTERVAL_MIN = int(os.getenv("CRAWL_INTERVAL_MIN", "30"))


def _ai_pipeline_job() -> None:
    db = SessionLocal()
    try:
        unsummarized = (
            db.query(Article)
            .filter(Article.original_content != None)  # noqa: E711
            .filter(Article.one_line_summary == None)  # noqa: E711
            .all()
        )
        logger.info("AI 파이프라인: 요약 대상 %d개", len(unsummarized))
        for article in unsummarized:
            try:
                summarize_article(article.id, db)
            except Exception:  # noqa: BLE001
                logger.exception("요약 실패: %s", article.id)

        unembedded = (
            db.query(Article)
            .filter(Article.one_line_summary != None)  # noqa: E711
            .filter(~exists().where(ArticleKeyword.article_id == Article.id))
            .all()
        )
        logger.info("AI 파이프라인: 임베딩 대상 %d개", len(unembedded))
        for article in unembedded:
            try:
                embed_article(article.id, article.title, article.paragraph_summary, db)
            except Exception:  # noqa: BLE001
                logger.exception("임베딩 실패: %s", article.id)
    finally:
        db.close()


def _crawl_job() -> None:
    logger.info("crawl job 시작")
    try:
        result = run_crawl()
        logger.info(
            "crawl job 완료: ok=%s total_new=%s",
            result.get("ok"),
            result.get("total_new"),
        )
    except Exception:  # noqa: BLE001 — 스케줄러 스레드가 죽지 않도록.
        logger.exception("crawl job 실패")
        return

    if not settings.enable_ai_pipeline:
        logger.info("AI 파이프라인 비활성화 (ENABLE_AI_PIPELINE=false) — 요약/임베딩 스킵")
        return

    try:
        _ai_pipeline_job()
    except Exception:  # noqa: BLE001
        logger.exception("AI 파이프라인 실패")


def start_scheduler():
    # 첫 시작 시 카테고리/서브카테고리 시드 보장.
    try:
        ensure_categories_seeded()
    except Exception:  # noqa: BLE001 — DB 미기동 환경에서 부팅 차단 방지.
        logger.exception("카테고리 시드 실패 — 스케줄러는 계속 진행")

    scheduler.add_job(
        _crawl_job,
        "interval",
        minutes=CRAWL_INTERVAL_MIN,
        id="crawl",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("scheduler started (crawl every %d min)", CRAWL_INTERVAL_MIN)
