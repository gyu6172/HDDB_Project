from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text
from app.core.config import settings
from app.core.database import get_db
from app.models.article import Article
from app.schemas.article import ArticleCard, SearchResultCard, SearchResultResponse
from app.schemas.common import ErrorResponse
from app.services.embedder import embed_query

router = APIRouter()


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)
    sort: Literal["relevance", "latest"] = "relevance"

    model_config = {
        "json_schema_extra": {
            "example": {"query": "부산항 물동량", "sort": "relevance"}
        }
    }


@router.post(
    "",
    response_model=SearchResultResponse,
    summary="마스코트 의미 검색",
    responses={422: {"model": ErrorResponse, "description": "요청 본문 검증 실패"}},
)
def mascot_search(body: SearchRequest, db: Session = Depends(get_db)):
    query_vector = embed_query(body.query)

    rows = db.execute(
        text("""
            WITH ranked AS (
                SELECT article_id,
                       MIN(embedding <=> CAST(:vec AS vector)) AS min_dist
                FROM article_keywords
                GROUP BY article_id
                HAVING MIN(embedding <=> CAST(:vec AS vector)) < :threshold
                ORDER BY min_dist
                LIMIT :limit
            )
            SELECT article_id, min_dist FROM ranked
        """),
        {
            "vec": str(query_vector),
            "threshold": settings.search_threshold,
            "limit": settings.search_top_k,
        },
    ).fetchall()

    if not rows:
        return SearchResultResponse(items=[])

    article_ids = [r.article_id for r in rows]
    order = {aid: i for i, aid in enumerate(article_ids)}
    similarity_map = {r.article_id: round(1 - r.min_dist, 4) for r in rows}

    articles = (
        db.query(Article)
        .options(
            joinedload(Article.category_rel),
            joinedload(Article.subcategory_rel),
        )
        .filter(Article.id.in_(article_ids))
        .all()
    )
    if body.sort == "latest":
        articles.sort(key=lambda a: a.published_at, reverse=True)
    else:
        articles.sort(key=lambda a: order[a.id])

    return SearchResultResponse(
        items=[
            SearchResultCard.model_validate(
                {
                    **a.__dict__,
                    "category_rel": a.category_rel,
                    "subcategory_rel": a.subcategory_rel,
                    "similarity": similarity_map[a.id],
                }
            )
            for a in articles
        ]
    )
