import logging
import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.services.crawler import ensure_categories_seeded, run_crawl

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

# 크롤링 주기는 환경변수로 조정 가능 (기본 30분).
CRAWL_INTERVAL_MIN = int(os.getenv("CRAWL_INTERVAL_MIN", "30"))


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
