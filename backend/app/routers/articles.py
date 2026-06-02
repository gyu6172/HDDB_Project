from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.models.article import Article
from app.models.category import Category, Subcategory
from app.schemas.article import ArticleCard, ArticleDetail, ArticleListResponse
from app.schemas.common import ErrorResponse

router = APIRouter()


@router.get(
    "",
    response_model=ArticleListResponse,
    summary="카테고리별 기사 목록 (커서 페이지네이션)",
    responses={422: {"model": ErrorResponse, "description": "요청 파라미터 검증 실패"}},
)
def list_articles(
    category:       str,
    subcategory:    str | None = None,
    sort:           Literal["recent", "confidence"] = "recent",
    min_confidence: float = Query(default=0.0, ge=0.0, le=1.0),
    limit:          int = Query(default=20, le=100),
    cursor:         str | None = None,
    db:             Session = Depends(get_db),
):
    """기사 목록.

    - sort=recent (기본): 최신순(published_at DESC).
    - sort=confidence: 분류 신뢰도 높은 순(confidence DESC, NULL 은 마지막).
    - min_confidence: 이 값 미만의 기사는 제외 (0~1).
    - cursor: 마지막으로 본 article.id (페이지 경계).
    """
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
    if min_confidence > 0:
        query = query.filter(Article.confidence >= min_confidence)
    if cursor:
        query = query.filter(Article.id > cursor)

    if sort == "confidence":
        # confidence 동률 시 최신순, 그것도 동률이면 id 로 안정 정렬.
        query = query.order_by(
            Article.confidence.desc().nullslast(),
            Article.published_at.desc(),
            Article.id.asc(),
        )
    else:
        query = query.order_by(Article.published_at.desc(), Article.id.asc())

    items = query.limit(limit).all()
    next_cursor = items[-1].id if len(items) == limit else None

    return ArticleListResponse(items=items, next_cursor=next_cursor)


@router.get(
    "/random",
    response_model=list[ArticleCard],
    summary="무작위 기사 (마스코트 말풍선용)",
)
def random_articles(
    limit: int = Query(default=10, le=50),
    db:    Session = Depends(get_db),
):
    """무작위 기사 목록.

    마스코트 말풍선에 one_line_summary 를 순환 노출하는 용도.
    요약(one_line_summary)이 없는 기사는 제외한다.
    프론트는 진입 시 한 번 받아두고 클라이언트에서 순환시키면 된다.

    NOTE: 이 라우트는 반드시 ``/{article_id}`` 보다 먼저 선언돼야 한다.
    (그렇지 않으면 "random" 이 article_id 로 해석된다.)
    """
    return (
        db.query(Article)
        .options(
            joinedload(Article.category_rel),
            joinedload(Article.subcategory_rel),
        )
        .filter(Article.one_line_summary.isnot(None))
        .order_by(func.random())
        .limit(limit)
        .all()
    )


@router.get(
    "/{article_id}",
    response_model=ArticleDetail,
    summary="기사 상세",
    responses={404: {"model": ErrorResponse, "description": "기사를 찾을 수 없음"}},
)
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
