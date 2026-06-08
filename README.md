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

## 로컬 실행 (Quickstart)

> 최소 실행 흐름만 정리. 상세 옵션·환경변수는 각 디렉터리 README 참고.
> 프론트는 백엔드 API에 의존하므로 **백엔드를 먼저 실행**하세요.

### 1) 백엔드 (먼저 실행)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows  (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env           # Windows  (Mac/Linux: cp .env.example .env)
uvicorn app.main:app --reload --port 8000
```

> ⚠️ **`.env.example` 복사만으로는 동작하지 않습니다.** `.env`를 열어 아래 값을 실제 값으로 채워야 합니다.
> - `DATABASE_URL`의 `[PASSWORD]` → 팀 채널에서 공유받은 **Supabase 비밀번호** (없으면 DB 연결 실패)
> - `GEMINI_API_KEY` → 요약·임베딩·**검색**에 필요 (비워 두면 해당 기능 동작 안 함)
> - (선택) 크롤링의 분류 단계까지 돌리려면 로컬 **Ollama 서버** 실행 필요. 크롤러만 점검할 땐 `.env`의 `ENABLE_AI_PIPELINE=false`.

- 헬스체크: http://localhost:8000/health · Swagger: http://localhost:8000/docs

### 2) 프론트엔드 (백엔드가 떠 있어야 함)

```bash
cd frontend
npm install
npm run dev
```

> `.env.local`은 **선택**입니다. 백엔드 주소가 기본값(`http://localhost:8000`)이면 설정 없이 동작하고, 다를 때만 `NEXT_PUBLIC_API_BASE_URL`을 지정하세요.

- 화면: http://localhost:3000

## 문서

- [기획 가이드라인](./hddb_guidelines.md)
- [통합 계약 (architecture)](./docs/architecture.md)
- [기여 가이드 (CONTRIBUTING)](./CONTRIBUTING.md)
