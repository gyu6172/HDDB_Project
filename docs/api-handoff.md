# API 연동 핸드오프 문서

프론트 ↔ 백엔드 API 연동을 위한 **결정사항·화면별 담당·주의점** 문서.

> ⚠️ **이 문서는 API 명세 원본이 아닙니다.**
> 요청/응답의 정확한 형태·필드·예시는 항상 **Swagger(자동 생성)**를 진실의 출처로 보세요.
> 이 문서는 Swagger가 담지 못하는 것 — **합의된 결정, 화면별 담당, mock→실제 전환 시 주의점** — 만 다룹니다.

---

## 0. 명세 확인 방법 (진실의 출처)

백엔드를 띄운 뒤:

- **Swagger UI**: http://localhost:8000/docs — 요청/응답/예시 직접 확인
- **OpenAPI 원본**: http://localhost:8000/openapi.json
- **TS 타입 자동 생성**(선택):
  ```
  npx openapi-typescript http://localhost:8000/openapi.json -o src/types/api.ts
  ```

코드(스키마)가 바뀌면 Swagger는 자동 반영됩니다. 이 md는 수동이라 늙을 수 있으니 **형태는 Swagger 기준**.

---

## 1. 공통 규약

- **Base URL**: `http://localhost:8000` (로컬). 프론트 `.env.local`의 `NEXT_PUBLIC_API_BASE_URL` 사용 권장.
- **CORS**: 백엔드에서 `localhost:3000` 허용 완료 → 브라우저 차단 없음.
- **응답 JSON 필드**: `camelCase` (예: `oneLineSummary`, `publishedAt`, `thumbnailUrl`).
- **요청 쿼리 파라미터**: `snake_case` (예: `min_confidence`).
- **목록 응답 래핑**: `{ items, nextCursor }` 형태.
- **에러 응답**: 4xx/5xx는 항상 `{ "detail": "..." }` (ErrorResponse).

### 공통 카드 형태 (`ArticleCard`)

```json
{
  "id": "3f1c9b7e-...",
  "title": "...",
  "oneLineSummary": "...",
  "cardSummary": "...",
  "source": "BBC",
  "sourceLang": "en",
  "publishedAt": "2026-05-30T09:00:00",
  "thumbnailUrl": "https://.../thumb.jpg",
  "category": "sea",
  "subcategory": "shipping",
  "confidence": 0.873
}
```

- `confidence`는 **`null`일 수 있음** (`number | null`).
- 검색 결과 카드(`SearchResultCard`)는 여기에 `similarity`(0~1)가 추가됨.

---

## 2. 합의된 결정사항

### 2-1. 정렬(sort) 파라미터 — 단어 3개 체계

| 값                                  | 의미            | `/articles` | `/search` |
| ----------------------------------- | --------------- | :---------: | :-------: |
| `recent` _(→ `latest`로 통일 권장)_ | 최신순          |     ✅      |    ✅     |
| `confidence`                        | 분류 신뢰도순   |     ✅      |    ❌     |
| `relevance`                         | 검색어 유사도순 |     ❌      |    ✅     |

- **카테고리 화면**: UI "관련도순" → API엔 **`sort=confidence`로 전송**. (UI 라벨은 그대로 둬도 됨)
- **검색 화면**: `sort=relevance` / `sort=latest` 그대로 사용.
- `relevance`는 **검색(유사도) 전용** — 카테고리에 보내면 422.
- **(권장) "최신순"은 `latest`로 통일하는 것을 권장.** 현재 `/articles`=`recent`, `/search`=`latest`로 갈리는데, `/search`가 이미 `latest`를 쓰므로 `/articles`의 `recent`를 `latest`로 맞추면 "한 동작 = 한 단어"가 깔끔하게 정리됨. (백엔드 `/articles` sort 값 변경 + 프론트 합의 필요, 동작 자체엔 영향 없음)

### 2-2. 검색 페이지네이션/필터/카운트 — 방향 A (클라이언트 처리)

- `/search`는 유사도 상위 **최대 100건**(`SEARCH_TOP_K`) 반환.
- 프론트가 받은 결과 안에서 **카테고리 필터 + 카운트 + 페이지네이션**을 처리.
- **카운트 의미 = "검색 결과 기준"** 분포 (DB 전체 매칭 기준 아님).
- 백엔드는 category 파라미터/카운트를 **제공하지 않음** (방향 A라 불필요).

---

## 3. 화면별 담당 & 필요한 API

### 🟦 유민 — 메인화면

호출 API **2개** (+ 검색 진입은 라우팅만).

**① 카테고리 섹션 (하늘/땅/바다)** — `GET /articles`

```
GET /articles?category=sky&limit=3&sort=recent
GET /articles?category=land&limit=3
GET /articles?category=sea&limit=3
```

- 응답: `{ items: ArticleCard[], nextCursor }`
- 섹션(`NewsItem`)이 쓰는 필드: `title`, `source`, `publishedAt`
- 응답은 배열이 아니라 **`{ items }`** → `res.items`로 꺼낼 것
- mock의 `time`("2시간 전")은 없음 → `publishedAt`(ISO)로 **상대시간 계산** 필요
- `nextCursor`는 메인에선 미사용

**② 마스코트 말풍선 (무작위 요약)** — `GET /articles/random`

```
GET /articles/random?limit=10
```

- 응답: **`ArticleCard[]` (배열, 래퍼 없음)**
- 진입 시 1번 호출 → 받은 10건의 `oneLineSummary`를 **5초마다 순환** 노출 (재호출 ❌)
- 요약 없는 기사는 백엔드가 제외함
- 현재 `MascotArea`는 정적 텍스트만 있음 → fetch + 타이머 + 표시 **신규 구현 필요**

**라우팅만 (API 아님)**: SearchDock·헤더 검색 → `/search?q=...`로 이동. 실제 검색은 건우 담당.

---

### 🟩 소리 — 카테고리화면 / 기사 상세화면

**① 카테고리 목록** — `GET /articles`

```
GET /articles?category=sea&subcategory=shipping&sort=confidence&limit=9&cursor=<id>
```

- `category`(필수), `subcategory`, `sort`(`recent`|`confidence`), `min_confidence`, `limit`, `cursor`
- 응답: `{ items: ArticleCard[], nextCursor }`
- **커서 페이지네이션**: 다음 페이지는 응답의 `nextCursor`를 `cursor`로 전달. `null`이면 마지막.

**② 기사 상세** — `GET /articles/{id}`

- 응답: `ArticleDetail` = `ArticleCard` + `originalUrl`, `content`, `paragraphSummaries`
- `paragraphSummaries` 항목 형태(**camelCase**):
  ```json
  { "paragraphIndex": 0, "originalText": "...", "summary": "..." }
  ```
- 없는 id → `404 { detail }`

**소리가 처리할 주의점**

- **#1** "관련도순" → API엔 `sort=confidence`로 변환해서 전송 (UI/URL은 그대로 OK)
- **#2** 목록 응답을 `res.items`로 받기 (현재 `api.ts`는 `Article[]` 기대 → 수정)
- **#7** 문단요약 필드명: 프론트 타입이 `paragraph_index`(snake) → 백엔드는 `paragraphIndex`(camel)로 옴. 타입 수정 필요
- **#6** `confidence` 타입을 `number | null`로

---

### 🟧 건우 — 검색화면

**검색** — `POST /search`

```
POST /search
Content-Type: application/json
{ "query": "부산항 물동량", "sort": "relevance" }
```

- `sort`: `relevance`(유사도) | `latest`(최신). **요청 본문(body)**에 넣음 (쿼리스트링 아님)
- 응답: `{ items: SearchResultCard[] }` — 유사도 상위 **최대 100건**
- `SearchResultCard` = `ArticleCard` + `similarity`(0~1)

**건우가 처리할 주의점 (방향 A)**

- **#3** 카테고리 필터 + 탭별 카운트 + 페이지네이션을 **받은 items 안에서** 처리
  - 카운트는 `getSearchCategoryCounts`를 **mockArticles가 아닌 받은 결과** 기준으로 수정
  - 페이지네이션은 결과를 N개씩 슬라이스 (커서 아님)
- **#4** 검색은 **서버 정렬 순서(유사도)를 그대로 사용** — `confidence`로 재정렬하는 코드 제거. "관련도순"은 `similarity` 기준
- **#5** 프론트 `Article` 타입에 `similarity`가 없음 → 검색용 타입(`extends Article { similarity }`) 추가
- 헤더/메인에서 넘어온 `q` 파라미터로 검색 수행

---

## 4. mock→실제 전환 공통 주의점 (요약)

> `#1`~`#7`은 코드 분석에서 찾은 **mock→실제 전환 시 문제**에 매긴 **내부 추적용 번호**(공식 표준 아님).
> `#1`~`#3`은 **HIGH(연결 즉시 깨짐)**, `#4`~`#7`은 **MEDIUM(조용히 값이 틀어짐)**.
> 프론트가 각 항목을 수정하면 해당 번호를 지워나가면 됩니다.

### 🔴 HIGH — 연결 즉시 깨짐

| #   | 제목                  | 내용                                                                          | 주 담당   |
| --- | --------------------- | ----------------------------------------------------------------------------- | --------- |
| 1   | 카테고리 정렬 422     | 프론트 `sort=relevance` vs 백엔드 `confidence`만 허용 → 호출 시 변환 필요     | 소리      |
| 2   | 응답 래퍼 불일치      | 목록은 `{items,nextCursor}` (`Article[]` 아님) → `res.items`로 받기           | 유민·소리 |
| 3   | 검색 필터/카운트 없음 | 백엔드 `/search`엔 category/카운트 없음 → 받은 결과로 클라이언트 처리(방향 A) | 건우      |

### 🟡 MEDIUM — 조용히 값이 틀어짐

| #   | 제목                 | 내용                                                                                                                                                    | 주 담당 |
| --- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| 4   | 가짜 relevance 정렬  | 검색 "관련도순"이 `similarity`가 아닌 `confidence`로 정렬됨 → 서버순서/similarity 사용                                                                  | 건우    |
| 5   | similarity 타입 없음 | 프론트 `Article` 타입에 `similarity` 부재 → 검색용 타입 추가                                                                                            | 건우    |
| 6   | confidence 타입      | 현재 DB 262행 모두 값 있음(null 0개). 단 컬럼·스키마는 nullable → 프론트 `number\|null` 권장 _(또는 백엔드 NOT NULL 강제 시 `number`로 확정 — 논의 중)_ | 공용    |
| 7   | 문단요약 필드명      | 프론트 `paragraph_index`(snake) vs 백엔드 `paragraphIndex`(camel)                                                                                       | 소리    |

---

## 5. 엔드포인트 한눈 정리

| Method | Path               | 용도                       | 응답                    |
| ------ | ------------------ | -------------------------- | ----------------------- |
| GET    | `/articles`        | 카테고리 목록 / 메인 섹션  | `{ items, nextCursor }` |
| GET    | `/articles/random` | 마스코트 무작위 기사       | `ArticleCard[]`         |
| GET    | `/articles/{id}`   | 기사 상세                  | `ArticleDetail`         |
| GET    | `/categories`      | 카테고리/서브카테고리 트리 | `CategorySchema[]`      |
| POST   | `/search`          | 마스코트 의미 검색         | `{ items }` (상위 ≤100) |

정확한 파라미터·필드·예시는 **/docs(Swagger)** 참고.
