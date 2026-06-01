from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import articles, categories, search
from app.scheduler.jobs import start_scheduler

tags_metadata = [
    {"name": "articles", "description": "기사 목록(커서 페이지네이션) 및 상세 조회."},
    {"name": "categories", "description": "카테고리/서브카테고리 트리 조회."},
    {"name": "search", "description": "마스코트 의미 기반 검색."},
]

app = FastAPI(
    title="HDDB API",
    version="0.1.0",
    description=(
        "HDDB 뉴스 서비스 백엔드 API.\n\n"
        "- 응답 JSON 필드는 camelCase, 요청 쿼리 파라미터는 snake_case 를 사용한다.\n"
        "- 목록 응답은 `{ items, nextCursor }` 형태로 래핑된다.\n"
        "- 비정상 응답(4xx/5xx)은 항상 `{ detail }` 형태(ErrorResponse)를 따른다."
    ),
    openapi_tags=tags_metadata,
    servers=[{"url": "http://localhost:8000", "description": "로컬 개발 서버"}],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(articles.router, prefix="/articles", tags=["articles"])
app.include_router(categories.router, prefix="/categories", tags=["categories"])
app.include_router(search.router, prefix="/search", tags=["search"])


@app.on_event("startup")
async def startup():
    start_scheduler()


@app.get("/health")
def health():
    return {"status": "ok"}
