from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.article import Article
from app.schemas.article import ArticleCard, ArticleDetail, ArticleListResponse

router = APIRouter()


@router.get("", response_model=ArticleListResponse)
def list_articles(
    category:    str,
    subcategory: str | None = None,
    limit:       int = Query(default=20, le=100),
    cursor:      str | None = None,
    db:          Session = Depends(get_db),
):
    query = db.query(Article).filter(Article.category == category)
    if subcategory:
        query = query.filter(Article.subcategory == subcategory)
    if cursor:
        query = query.filter(Article.id > cursor)

    items = query.order_by(Article.published_at.desc()).limit(limit).all()
    next_cursor = items[-1].id if len(items) == limit else None

    return ArticleListResponse(items=items, next_cursor=next_cursor)


@router.get("/{article_id}", response_model=ArticleDetail)
def get_article(article_id: str, db: Session = Depends(get_db)):
    return db.query(Article).filter(Article.id == article_id).first()
