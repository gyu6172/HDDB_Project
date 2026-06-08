# HDDB 백엔드

하늘/땅/바다 뉴스 큐레이션 서비스 백엔드 API 서버입니다.

## 기술 스택

- **FastAPI** — REST API 서버
- **SQLAlchemy + Alembic** — ORM + DB 마이그레이션
- **PostgreSQL (Supabase)** — 팀 공용 데이터베이스 (pgvector 포함)
- **APScheduler** — 크롤링 스케줄러

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
│   ├── models/              # SQLAlchemy 테이블 정의
│   ├── schemas/             # Pydantic 요청/응답 스키마
│   ├── routers/             # API 엔드포인트
│   ├── services/            # 크롤러, AI 요약 로직
│   ├── scheduler/           # 크롤링 스케줄러
│   └── main.py
├── alembic/                 # DB 마이그레이션
├── docker-compose.yml       # DB 컨테이너 설정
├── .env                     # 환경변수 (git 제외)
├── .env.example             # 환경변수 템플릿
└── requirements.txt
```

## API 엔드포인트

| Method | 경로             | 설명                        |
| ------ | ---------------- | --------------------------- |
| GET    | `/health`        | 헬스체크                    |
| GET    | `/articles`      | 기사 리스트 (category 필수) |
| GET    | `/articles/{id}` | 기사 상세                   |
| GET    | `/categories`    | 카테고리 트리               |
| POST   | `/search`        | 마스코트 검색               |
