from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.models.article import Article
from app.models.category import Category, Subcategory
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
    query = (
        db.query(Article)
        .join(Article.category_rel)
        .join(Article.subcategory_rel)
        .options(
            joinedload(Article.category_rel),
            joinedload(Article.subcategory_rel),
        )
        .filter(Category.key == category)
    )
    if subcategory:
        query = query.filter(Subcategory.key == subcategory)
    if cursor:
        query = query.filter(Article.id > cursor)

    items = query.order_by(Article.published_at.desc()).limit(limit).all()
    next_cursor = items[-1].id if len(items) == limit else None

    return ArticleListResponse(items=items, next_cursor=next_cursor)


@router.get("/{article_id}", response_model=ArticleDetail)
def get_article(article_id: str, db: Session = Depends(get_db)):
    article = (
        db.query(Article)
        .options(
            joinedload(Article.category_rel),
            joinedload(Article.subcategory_rel),
        )
        .filter(Article.id == article_id)
        .first()
    )
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")

    return article
