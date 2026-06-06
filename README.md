# HDDB (가칭)

자연을 **하늘/땅/바다** 세 영역으로 분류해 뉴스를 큐레이션하고, AI가 요약본을 제공하는 개인화 뉴스 플랫폼입니다.

## 디렉터리

```
frontend/   # 사용자 화면 · 마스코트 인터랙션   (Next.js · React · TypeScript · Tailwind)
backend/    # 수집 · 분류/요약 · API            (FastAPI · SQLAlchemy · Gemini)
docs/       # 통합 계약 등 문서
.github/    # PR/이슈 템플릿
```

데이터베이스는 팀 공용 **Supabase**(PostgreSQL + pgvector)를 사용합니다.

## 셋업 (개념 흐름 — 구체 명령은 각 디렉터리 README)

1. `backend/` 의존성 설치 후 실행 → 공용 Supabase에 연결 (로컬 DB 설치 불필요, [`backend/README.md`](./backend/README.md))
2. `frontend/` 의존성 설치 후 실행 → 백엔드에 연결 ([`frontend/README.md`](./frontend/README.md))

## 문서

- [기획 가이드라인](./hddb_guidelines.md)
- [통합 계약 (architecture)](./docs/architecture.md)
- [기여 가이드 (CONTRIBUTING)](./CONTRIBUTING.md)
