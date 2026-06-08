# HDDB 프론트엔드

하늘/땅/바다 뉴스 큐레이션 서비스의 사용자 화면 · 마스코트 인터랙션을 담당하는 프론트엔드입니다.

## 기술 스택

- **Next.js 16** (App Router) — React 프레임워크
- **React 19**
- **TypeScript**
- **Tailwind CSS 4** — 스타일링

---

## 사전 준비

- Node.js 20 이상
- **백엔드 서버가 실행 중이어야 합니다** (기본 `http://localhost:8000`). 실행 방법은 [`backend/README.md`](../backend/README.md) 참고.

---

## 초기 설정

### 1. 패키지 설치

```bash
npm install
```

### 2. 환경변수 설정 (선택)

백엔드 주소가 기본값(`http://localhost:8000`)과 다를 때만 설정하면 됩니다.

`.env.local` 파일을 만들고 아래를 추가하세요.

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

> 설정하지 않으면 `http://localhost:8000`을 기본값으로 사용합니다 (`src/lib/api.ts`).

### 3. 개발 서버 실행

```bash
npm run dev
```

[http://localhost:3000](http://localhost:3000) 에서 확인할 수 있습니다.

---

## 스크립트

| 명령              | 설명                       |
| ----------------- | -------------------------- |
| `npm run dev`     | 개발 서버 실행 (port 3000) |
| `npm run build`   | 프로덕션 빌드              |
| `npm run start`   | 빌드 결과 실행             |
| `npm run lint`    | ESLint 검사                |

---

## 폴더 구조

```
frontend/
├── src/
│   ├── app/                  # App Router 페이지
│   │   ├── page.tsx          # 스플래시 (→ /main)
│   │   ├── main/             # 메인 화면 (하늘/땅/바다 + 마스코트)
│   │   ├── category/[category]/  # 카테고리별 기사 목록
│   │   ├── articles/[id]/    # 기사 상세
│   │   ├── search/           # 마스코트 검색 결과
│   │   ├── layout.tsx
│   │   └── globals.css
│   ├── components/           # 화면별 컴포넌트 (common/main/search/...)
│   ├── lib/                  # API 클라이언트(api.ts), 검색, mock 데이터
│   ├── constants/            # 카테고리/서브카테고리 메타데이터
│   └── types/                # 공용 타입 (article.ts)
└── public/images/            # 배경·서브카테고리 기본 이미지
```

## API 연동

- API 클라이언트: `src/lib/api.ts` (`fetchArticlesByCategory`, `fetchRandomArticles`, `fetchArticleById` 등)
- 응답 JSON 필드는 **camelCase**, 목록 응답은 `{ items, nextCursor }` 형태입니다.
- 정확한 요청/응답 형태는 백엔드 실행 후 **Swagger** ([http://localhost:8000/docs](http://localhost:8000/docs))를 진실의 출처로 보세요.
