from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.category import Category
from app.schemas.category import CategorySchema

router = APIRouter()


@router.get(
    "",
    response_model=list[CategorySchema],
    summary="카테고리/서브카테고리 트리",
)
def get_category_tree(db: Session = Depends(get_db)):
    return db.query(Category).all()
