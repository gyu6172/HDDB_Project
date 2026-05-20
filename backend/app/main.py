from fastapi import FastAPI
from app.routers import articles, categories, search
from app.scheduler.jobs import start_scheduler

app = FastAPI(title="HDDB API")

app.include_router(articles.router, prefix="/articles", tags=["articles"])
app.include_router(categories.router, prefix="/categories", tags=["categories"])
app.include_router(search.router, prefix="/search", tags=["search"])


@app.on_event("startup")
async def startup():
    start_scheduler()


@app.get("/health")
def health():
    return {"status": "ok"}
