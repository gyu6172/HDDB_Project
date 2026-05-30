import os
from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.models.article import Article
from app.schemas.article import ArticleCard
from app.services.embedder import embed_query

router = APIRouter()

SEARCH_THRESHOLD = float(os.getenv("SEARCH_THRESHOLD", "0.5"))


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)
    sort: Literal["relevance", "latest"] = "relevance"


@router.post("", response_model=list[ArticleCard])
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
                LIMIT 20
            )
            SELECT article_id FROM ranked
        """),
        {"vec": str(query_vector), "threshold": SEARCH_THRESHOLD},
    ).fetchall()

    if not rows:
        return []

    article_ids = [r.article_id for r in rows]
    order = {aid: i for i, aid in enumerate(article_ids)}

    articles = db.query(Article).filter(Article.id.in_(article_ids)).all()
    if body.sort == "latest":
        articles.sort(key=lambda a: a.published_at, reverse=True)
    else:
        articles.sort(key=lambda a: order[a.id])

    return articles
