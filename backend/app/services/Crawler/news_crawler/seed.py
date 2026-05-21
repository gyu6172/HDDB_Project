"""CATEGORY_DEFS 를 메인 DB 의 categories/subcategories 테이블에 시드/동기화한다.

또한 config/sources.yaml 의 RSS 소스 목록을 yaml 로부터 읽어 반환한다.
메인 DB 에는 별도의 sources 테이블이 없으므로, 소스는 yaml 이 진실의 원천이다.
"""
from __future__ import annotations

from pathlib import Path

import yaml
from sqlalchemy import select

from .classifier import CATEGORY_DEFS
from .db import SessionLocal
from .models import Category, Subcategory

SOURCES_FILE = Path(__file__).resolve().parent.parent / "config" / "sources.yaml"

_GROUP_LABELS: dict[str, str] = {
    "sky": "하늘",
    "land": "땅",
    "sea": "바다",
}


def load_sources_from_yaml() -> list[dict]:
    if not SOURCES_FILE.exists():
        return []
    with SOURCES_FILE.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or []
    if not isinstance(data, list):
        raise ValueError(f"{SOURCES_FILE} must contain a list at the top level")
    return data


def sync_categories() -> tuple[int, int]:
    """Category(sky/land/sea) + Subcategory 를 시드한다.

    Returns (categories_added, subcategories_added)."""
    cat_added = sub_added = 0
    with SessionLocal() as session:
        for group_key, group_label in _GROUP_LABELS.items():
            existing = session.scalar(
                select(Category).where(Category.key == group_key)
            )
            if existing is None:
                session.add(Category(key=group_key, label=group_label))
                cat_added += 1
        session.flush()

        cats = {c.key: c for c in session.scalars(select(Category)).all()}
        for group, slug, label_ko, _desc in CATEGORY_DEFS:
            parent = cats.get(group)
            if parent is None:
                continue
            existing_sub = session.scalar(
                select(Subcategory).where(
                    Subcategory.category_id == parent.id,
                    Subcategory.key == slug,
                )
            )
            if existing_sub is None:
                session.add(
                    Subcategory(key=slug, label=label_ko, category_id=parent.id)
                )
                sub_added += 1
            else:
                if existing_sub.label != label_ko:
                    existing_sub.label = label_ko
        session.commit()
    return cat_added, sub_added
