"""config/sources.yaml 의 RSS 소스 목록을 DB에 시드/동기화한다."""
from __future__ import annotations

from pathlib import Path

import yaml
from sqlalchemy import select

from .db import SessionLocal
from .models import Source

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
