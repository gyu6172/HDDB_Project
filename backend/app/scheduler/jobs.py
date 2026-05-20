from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()


def start_scheduler():
    # TODO: 크롤링 주기 등록
    # scheduler.add_job(crawl_job, "interval", minutes=30)
    scheduler.start()
