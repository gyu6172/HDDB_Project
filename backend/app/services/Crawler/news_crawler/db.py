"""DB 엔진/세션: main project의 app.core.database 를 그대로 사용한다.

이전에는 별도 sqlite news.db 에 저장했지만, 이제는 메인 프로젝트의
PostgreSQL DB(또는 DATABASE_URL 로 설정된 어떤 DB든)에 직접 기사를 저장한다.
"""
from __future__ import annotations

from app.core.database import Base, SessionLocal, engine

__all__ = ["Base", "SessionLocal", "engine", "init_db"]


def init_db() -> None:
    """등록된 모든 모델로 테이블을 생성한다 (개발/테스트 편의용).

    운영 환경에서는 `alembic upgrade head` 로 마이그레이션을 적용하는 것이 정석이다.
    """
    import app.models.article  # noqa: F401
    import app.models.category  # noqa: F401

    Base.metadata.create_all(bind=engine)
