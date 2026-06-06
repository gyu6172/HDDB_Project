# HDDB 백엔드

하늘/땅/바다 뉴스 큐레이션 서비스 백엔드 API 서버입니다.

## 기술 스택

- **FastAPI** — REST API 서버
- **SQLAlchemy + Alembic** — ORM + DB 마이그레이션
- **PostgreSQL (Supabase)** — 팀 공용 데이터베이스 (pgvector 포함)
- **APScheduler** — 크롤링 스케줄러
- **Google Gemini (google-genai)** — 기사 요약 생성 및 검색용 임베딩
- **Ollama (로컬 LLM)** — 기사 카테고리 분류 (기본 `qwen2.5:3b`)
- **trafilatura** — 뉴스 본문 추출·정제

---

## 사전 준비

- Python 3.11 이상
- Supabase 공용 DB 비밀번호 (팀 채널에서 별도 공유)

> PostgreSQL은 별도 설치/실행 불필요합니다. 팀 공용 Supabase 인스턴스를 사용합니다.
> 오프라인 개발이 필요하면 `docker-compose.yml`로 로컬 DB를 띄울 수 있습니다 (선택).

---

## 초기 설정

### 1. 가상환경 생성 및 활성화

```bash
# Anaconda 사용자
pip install virtualenv
virtualenv .venv

# 일반 Python 사용자
python -m venv .venv
```

**활성화**

```bash
# Windows
.venv\Scripts\activate

# Mac / Linux
source .venv/bin/activate
```

프롬프트 앞에 `(.venv)` 가 붙으면 성공입니다.

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 환경변수 설정

`.env.example`을 복사해서 `.env` 파일을 만듭니다.

```bash
# Windows
copy .env.example .env

# Mac / Linux
cp .env.example .env
```

`.env` 파일을 열어 `DATABASE_URL` 의 `[PASSWORD]` 부분을 팀에서 공유받은 Supabase 비밀번호로 교체하세요.
비밀번호에 `!`, `^`, `@` 등 특수문자가 있다면 URL 인코딩(`%21`, `%5E`, `%40`)으로 바꿔야 합니다.

**환경변수 목록**

| 변수                 | 필수 | 기본값                                          | 설명                                                                 |
| -------------------- | ---- | ----------------------------------------------- | -------------------------------------------------------------------- |
| `DATABASE_URL`       | ✅   | —                                               | Supabase 연결 문자열                                                 |
| `PORT`               |      | `8000`                                          | API 서버 포트                                                        |
| `GEMINI_API_KEY`     | ⚠️   | (빈 값)                                         | 요약·임베딩에 필요. AI 파이프라인/검색을 쓰려면 설정                 |
| `ENABLE_AI_PIPELINE` |      | `true`                                          | 크롤링 후 요약·임베딩 자동 실행 여부 (크롤러 단독 테스트 시 `false`) |
| `SEARCH_THRESHOLD`   |      | `0.5`                                           | 검색 시 코사인 유사도 임계값                                         |
| `SEARCH_TOP_K`       |      | `100`                                           | 검색 시 반환할 상위 결과 개수                                        |
| `CORS_ORIGINS`       |      | `http://localhost:3000,http://127.0.0.1:3000`   | 쉼표로 구분된 CORS 허용 origin (prod 도메인은 여기에 추가)           |

### 4. DB 마이그레이션 (선택)

공용 DB에는 이미 최신 스키마가 적용되어 있습니다. 새 마이그레이션이 추가됐을 때만 실행하세요.

```bash
alembic upgrade head
```

### 5. 서버 실행

```bash
uvicorn app.main:app --reload --port 8000
```

서버가 실행되면 아래 주소에서 확인할 수 있습니다.

- API 헬스체크: [http://localhost:8000/health](http://localhost:8000/health)
- Swagger 문서: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## DB 관련 명령어

### 공용 DB (Supabase)

- 데이터/스키마 확인: [Supabase 대시보드](https://supabase.com/dashboard/project/qtowsnliucvptzzmkwul) → Table Editor
- 비밀번호 분실/변경: Project Settings → Database → Reset database password
- 연결 문자열 다시 받기: 상단 `Connect` 버튼 → `Session pooler`

### 로컬 DB (오프라인 개발 시에만)

```bash
# 로컬 DB 시작 (.env의 DATABASE_URL을 localhost로 변경 필요)
docker-compose up -d

# 로컬 DB 중지
docker-compose down

# 로컬 DB 초기화
docker-compose down -v
```

---

## 폴더 구조

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py        # 환경변수
│   │   └── database.py      # DB 세션
│   ├── models/              # SQLAlchemy 테이블 정의 (article/category/keyword)
│   ├── schemas/             # Pydantic 요청/응답 스키마
│   ├── routers/             # API 엔드포인트 (articles/categories/search)
│   ├── services/            # 크롤러·요약·임베딩 로직
│   │   ├── Crawler/             # RSS 기반 뉴스 크롤러
│   │   ├── trafilatura_crawler/ # 본문 추출·정제 파이프라인
│   │   ├── summarizer.py        # Gemini 요약 생성
│   │   └── embedder.py          # 검색용 임베딩
│   ├── scheduler/           # 크롤링 스케줄러 (APScheduler)
│   └── main.py
├── alembic/                 # DB 마이그레이션
├── scripts/                 # AI 파이프라인 실행·점검용 스크립트
├── docker-compose.yml       # 로컬 DB 컨테이너 설정 (선택)
├── .env                     # 환경변수 (git 제외)
├── .env.example             # 환경변수 템플릿
└── requirements.txt
```

## API 엔드포인트

응답 JSON 필드는 **camelCase**, 목록 응답은 `{ items, nextCursor }` 형태(커서 페이지네이션)입니다.
정확한 요청/응답 형태는 서버 실행 후 [Swagger](http://localhost:8000/docs)를 진실의 출처로 보세요.

| Method | 경로               | 설명                                                              |
| ------ | ------------------ | ----------------------------------------------------------------- |
| GET    | `/health`          | 헬스체크                                                          |
| GET    | `/articles`        | 기사 리스트. `category` 필수, `subcategory`·`sort`(`recent`/`confidence`)·`min_confidence`·`limit`·`cursor` 지원 |
| GET    | `/articles/random` | 무작위 기사 (마스코트 말풍선용)                                   |
| GET    | `/articles/{id}`   | 기사 상세                                                         |
| GET    | `/categories`      | 카테고리/서브카테고리 트리                                        |
| POST   | `/search`          | 마스코트 의미 검색 (`{ query, sort }`)                            |
