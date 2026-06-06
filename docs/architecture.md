# 아키텍처 (Architecture)

> HDDB의 **시스템 구성 · 데이터 파이프라인 · 데이터 모델 · API 계약**을 다룹니다.
> 제품 기획·UX·로드맵은 [`../hddb_guidelines.md`](../hddb_guidelines.md), 협업 규칙은 [`../CONTRIBUTING.md`](../CONTRIBUTING.md) 참고.
> 요청/응답의 정확한 형태는 항상 **Swagger**(`http://localhost:8000/docs`)를 진실의 출처로 보세요.

---

## 1. 시스템 개요

자연(하늘/땅/바다) 뉴스를 수집·분류·요약해 저장하고, 의미 기반 검색과 함께 제공하는 큐레이션 서비스입니다.

```
                  ┌─────────────────────── backend ───────────────────────┐
[RSS 소스] ─► 수집 ─► 분류 ─► 요약 ─► 임베딩 ─► [Supabase] ─► FastAPI ─► [Next.js 프론트]
            (trafilatura) (Ollama) (Gemini) (Gemini)   (PostgreSQL      │         마스코트 인터랙션
                                                        + pgvector)      │         로컬 관심사 재정렬
                                              마스코트 검색 ◄────────────┘
                                              (질의 임베딩 → 코사인 유사도)
```

| 레이어 | 기술 |
| ------ | ---- |
| 프론트엔드 | Next.js 16 (App Router) · React 19 · TypeScript · Tailwind CSS 4 |
| API | FastAPI · SQLAlchemy · Pydantic |
| 스케줄러 | APScheduler |
| 수집/정제 | feedparser(RSS) · trafilatura(본문 추출) |
| 분류 AI | 로컬 Ollama LLM (기본 `qwen2.5:3b`) + 키워드 사전 필터 |
| 요약·임베딩 AI | Google Gemini (`gemini-2.5-flash` 요약 / `gemini-embedding-001` 임베딩) |
| 데이터베이스 | Supabase — PostgreSQL + pgvector |

---

## 2. 데이터 파이프라인

APScheduler가 `CRAWL_INTERVAL_MIN`(기본 30분)마다 크롤 작업을 실행한다. 크롤 직후 `ENABLE_AI_PIPELINE=true`이면 요약·임베딩이 이어서 돈다.

### 2.1 수집 (Crawl)

- RSS 소스 목록은 `app/services/Crawler/config/sources.yaml`이 진실의 원천(별도 sources 테이블 없음).
- 영어/한국어 소스 병행. 본문은 **trafilatura**로 추출·정제.
- 중복은 `original_url` 유니크 제약으로 차단.

### 2.2 분류 (Classify)

- **1차 키워드 사전 필터**(`passes_prefilter`): 제목+본문에 자연 관련 키워드가 하나도 없으면 LLM 호출 없이 제외.
- **2차 LLM 분류**: 로컬 Ollama가 가장 적합한 **단일 서브카테고리 slug + confidence(0.000~1.000)** 부여. 자연과 무관하면 `null` → 저장 제외.
- 자연 기사만 `articles`에 저장하며, 서브카테고리의 상위 그룹(sky/land/sea)이 카테고리로 매핑된다.

> Ollama 서버가 꺼져 있으면 크롤 작업은 분류 단계에서 중단된다(`OllamaUnavailable`). 크롤러 단독 점검 시에는 `ENABLE_AI_PIPELINE=false`.

### 2.3 요약 (Summarize)

- 대상: `original_content`는 있고 `one_line_summary`가 없는 기사.
- **Gemini `gemini-2.5-flash`**가 한국어 요약 3종 생성(영어 기사도 한국어로):
  - `one_line_summary` (30~50자), `card_summary` (100자 내외), `paragraph_summary` (문단별 30~50자, JSON 배열)
- 마스코트 말투(친근한 존댓말 "~예요/~한답니다")를 프롬프트로 고정.

### 2.4 임베딩 (Embed)

- 대상: 요약은 있고 `article_keywords`가 없는 기사.
- **Gemini `gemini-embedding-001`**(3072차원)으로 **제목 + 문단별 요약 텍스트**를 각각 임베딩해 `article_keywords`에 저장(`task_type=RETRIEVAL_DOCUMENT`).

### 2.5 서빙 & 검색 (Serve & Search)

- FastAPI가 §5 API 제공.
- 검색은 질의를 임베딩(`RETRIEVAL_QUERY`)한 뒤 `article_keywords`와의 **pgvector 코사인 거리**를 기사별 최솟값으로 집계, 임계값(`SEARCH_THRESHOLD`) 미만 상위 `SEARCH_TOP_K`건 반환.

---

## 3. 데이터 모델

| 테이블 | 핵심 컬럼 |
| ------ | --------- |
| `categories` | `id`, `key`(`sky`/`land`/`sea`), `label` |
| `subcategories` | `id`, `key`, `label`, `category_id` — `(category_id, key)` 유니크 |
| `articles` | `id`, `title`, `original_url`(유니크), `original_content`, `source`, `source_lang`(`ko`/`en`), `published_at`, `thumbnail_url`, `category_id`, `subcategory_id`, `one_line_summary`, `card_summary`, `paragraph_summary`(JSON), `confidence`(0~1) |
| `article_keywords` | `id`, `article_id`(FK, CASCADE), `text`, `embedding`(`vector(3072)`) — 검색용 |

**문단별 요약 JSON 구조** (`paragraph_summary`):

```json
[{ "paragraph_index": 0, "original_text": "원문 문단...", "summary": "요약..." }]
```

> **서브카테고리 SSOT는 DB `subcategories` 테이블**이며, 분류기 `CATEGORY_DEFS`(9개: bird·space·weather / disaster·animal·ground_pollution / marine_life·deep_sea·ocean_pollution)로 시드된다.
> ⚠️ 프론트(`constants/category.ts`)는 추가로 `air_pollution`(sky)·`insect`(land)를 정의해 11개를 노출 — 분류기는 이 둘을 채우지 않으므로 정합성 정리가 필요하다.

---

## 4. 주요 기능의 기술 명세

- **카테고리 목록** (`GET /articles`): 카테고리/서브카테고리 필터 + 정렬(`recent`/`confidence`) + `min_confidence` 필터, **커서 페이지네이션**(`{ items, nextCursor }`).
- **기사 상세** (`GET /articles/{id}`): 메타 + 원문 전문 + 문단별 요약.
- **마스코트 말풍선** (`GET /articles/random`): 요약 있는 기사 무작위 — 프론트가 진입 시 받아 클라이언트에서 순환.
- **마스코트 검색** (`POST /search`): 임베딩 의미 검색(§2.5). `sort=relevance`(유사도순)/`latest`(최신순). 결과에 `similarity` 포함.
- **개인화**: 사용자 관심사는 **클라이언트 로컬 저장**(계정·서버 식별자 없음). 서버로 보내지 않고, 받은 결과를 클라이언트가 재정렬(관심 서브카테고리 상단 배치).

---

## 5. API 계약

> **형태**는 합의 대상. 응답 JSON 필드는 `camelCase`, 요청 쿼리 파라미터는 `snake_case`.

### 공통 규약

- **Base URL**: `http://localhost:8000` (로컬). 프론트 `.env.local`의 `NEXT_PUBLIC_API_BASE_URL` 사용.
- **CORS**: `CORS_ORIGINS`로 허용 origin 관리(기본 `localhost:3000`).
- **목록 응답 래핑**: `{ items, nextCursor }`.
- **에러 응답**: 4xx/5xx는 항상 `{ "detail": "..." }` (FastAPI 표준 ErrorResponse).

### 엔드포인트

| Method | 경로 | 입력 | 출력 |
| ------ | ---- | ---- | ---- |
| GET | `/health` | — | `{ "status": "ok" }` |
| GET | `/articles` | `category`(필수), `subcategory?`, `sort`(`recent`/`confidence`), `min_confidence`, `limit`, `cursor` | `{ items: ArticleCard[], nextCursor }` |
| GET | `/articles/random` | `limit` | `ArticleCard[]` |
| GET | `/articles/{id}` | — | `ArticleDetail` |
| GET | `/categories` | — | 카테고리+서브카테고리 트리 |
| POST | `/search` | `{ query, sort }` | `{ items: SearchResultCard[] }` (`similarity` 포함) |

- `ArticleCard`: `id, title, oneLineSummary, cardSummary?, source, sourceLang, publishedAt, thumbnailUrl, category, subcategory, confidence`
- `ArticleDetail`: `ArticleCard` + `content, originalUrl, paragraphSummaries`
- `sourceLang`(`ko|en`)는 원문 언어. 요약·표시 텍스트는 **항상 한국어**.

---

## 6. 공유 enum — 카테고리

| 내부 값 (저장·API 정본) | 표시 라벨 |
| ----------------------- | --------- |
| `sky` | 하늘 |
| `land` | 땅 |
| `sea` | 바다 |

저장·API는 `sky/land/sea`를 정본으로 사용. 한글은 표시 전용.

---

## 7. 핵심 원칙 & 결정 내역

### 사전 생성 원칙

요약(한줄/카드/문단별)은 **클릭 시점이 아니라 수집 시점에 미리 생성**해 저장한다. 클릭 시 AI 호출은 응답 지연으로 금지.

### 확정 결정 (회의)

- 사용자 식별 = 로컬 저장(계정·서버 식별자 없음)
- 다국어 = 영어 소스 병행 수집, 요약은 한국어
- AI = 분류는 로컬 Ollama, 요약·임베딩은 Gemini(무료 한도)
- 마스코트 = 멀티턴 없는 임베딩 의미 검색
- 원문 전문 저장·응답 = 팀플·미배포 한정 ([`../hddb_guidelines.md §5.1`](../hddb_guidelines.md) 【팀 결정 2026-05-15】)

### 통합 시 확정·구현 완료

- [x] 문단별 요약 구조: `{ paragraphIndex, originalText, summary }` 객체 배열
- [x] 표현 필드 책임: 썸네일은 백엔드 저장·제공(`thumbnailUrl`), 상대시각 표시는 프론트
- [x] 서브카테고리 SSOT: DB `subcategories` 테이블 (`GET /categories`) — §3 정합성 주의 참조
- [x] 개인화 전달: 서버 미전송, 클라이언트 재정렬
