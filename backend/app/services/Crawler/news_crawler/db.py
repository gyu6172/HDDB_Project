"""DB 엔진/세션 설정. DATABASE_URL 환경변수로 어떤 DB든 연결 가능."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///news.db")

# SQLite는 멀티스레드 옵션이 필요. 다른 DB는 영향 없음.
_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=_connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    """등록된 모든 모델로부터 테이블을 생성한다(이미 있으면 그대로 둠)."""
    # SQLite 파일 경로가 상대경로면 프로젝트 루트 기준으로 만들어 둔다.
    if DATABASE_URL.startswith("sqlite:///") and not DATABASE_URL.startswith("sqlite:////"):
        db_file = DATABASE_URL.replace("sqlite:///", "", 1)
        Path(db_file).parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
