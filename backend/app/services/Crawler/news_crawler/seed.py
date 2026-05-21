"""config/sources.yaml 의 RSS 소스 목록을 DB에 시드/동기화한다."""
from __future__ import annotations

from pathlib import Path

import yaml
from sqlalchemy import select

from .classifier import CATEGORY_DEFS
from .db import SessionLocal
from .models import Category, Source

SOURCES_FILE = Path(__file__).resolve().parent.parent / "config" / "sources.yaml"


def load_sources_from_yaml() -> list[dict]:
    if not SOURCES_FILE.exists():
        return []
    with SOURCES_FILE.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or []
    if not isinstance(data, list):
        raise ValueError(f"{SOURCES_FILE} must contain a list at the top level")
    return data


def sync_sources() -> tuple[int, int]:
    """YAML → DB. 새 소스는 추가, 기존 소스는 name/language를 갱신.

    Returns (added, updated)."""
    items = load_sources_from_yaml()
    added = updated = 0
    with SessionLocal() as session:
        for item in items:
            url = item["url"].strip()
            name = item["name"].strip()
            language = item["language"].strip().lower()

            existing = session.scalar(select(Source).where(Source.url == url))
            if existing is None:
                session.add(Source(name=name, url=url, language=language, active=True))
                added += 1
            else:
                changed = False
                if existing.name != name:
                    existing.name = name
                    changed = True
                if existing.language != language:
                    existing.language = language
                    changed = True
                if changed:
                    updated += 1
        session.commit()
    return added, updated


def sync_categories() -> int:
    """classifier.CATEGORY_DEFS 를 categories 테이블에 시드/동기화. 추가된 행 수 반환."""
    added = 0
    with SessionLocal() as session:
        for group, slug, label_ko, _desc in CATEGORY_DEFS:
            existing = session.scalar(select(Category).where(Category.slug == slug))
            if existing is None:
                session.add(Category(slug=slug, group=group, label_ko=label_ko))
                added += 1
            else:
                # 라벨/그룹은 코드 정의가 진실의 원천.
                if existing.group != group:
                    existing.group = group
                if existing.label_ko != label_ko:
                    existing.label_ko = label_ko
        session.commit()
    return added
