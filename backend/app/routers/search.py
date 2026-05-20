from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.article import ArticleCard

router = APIRouter()


@router.post("", response_model=list[ArticleCard])
def mascot_search(body: dict, db: Session = Depends(get_db)):
    # TODO: 자연어 → 키워드 축약 → 기사 검색
    return []
