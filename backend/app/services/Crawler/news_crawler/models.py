"""크롤러 내부에서 사용하는 모델은 메인 프로젝트의 모델을 그대로 재사용한다.

기존 자체 정의(Article/Category/Source)는 메인 스키마(Article/Category/Subcategory)
로 대체되었다. 다른 크롤러 모듈에서 `from .models import Article, Category, Subcategory`
형태로 import 할 수 있도록 re-export 한다.
"""
from __future__ import annotations

from app.models.article import Article
from app.models.category import Category, Subcategory

__all__ = ["Article", "Category", "Subcategory"]
