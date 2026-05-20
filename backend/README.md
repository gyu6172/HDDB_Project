# HDDB 백엔드

하늘/땅/바다 뉴스 큐레이션 서비스 백엔드 API 서버입니다.

## 기술 스택

- **FastAPI** — REST API 서버
- **SQLAlchemy + Alembic** — ORM + DB 마이그레이션
- **PostgreSQL** — 데이터베이스 (Docker로 실행)
- **APScheduler** — 크롤링 스케줄러

---

## 사전 준비

- Python 3.11 이상
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) 설치 및 실행 중

> PostgreSQL은 별도 설치 불필요합니다. Docker로 실행합니다.

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

`.env` 파일은 수정 없이 그대로 사용해도 됩니다.

### 4. DB 실행

```bash
docker-compose up -d
```

### 5. DB 마이그레이션

```bash
alembic upgrade head
```

### 6. 서버 실행

```bash
uvicorn app.main:app --reload --port 8000
```

서버가 실행되면 아래 주소에서 확인할 수 있습니다.

- API 헬스체크: [http://localhost:8000/health](http://localhost:8000/health)
- Swagger 문서: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## DB 관련 명령어

```bash
# DB 시작
docker-compose up -d

# DB 중지
docker-compose down

# DB 초기화 (데이터 전부 삭제)
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
