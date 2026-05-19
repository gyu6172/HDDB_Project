# HDDB (가칭)

자연을 **하늘/땅/바다** 세 영역으로 분류해 뉴스를 큐레이션하고, AI가 요약본을 제공하는 개인화 뉴스 플랫폼입니다.

## 디렉터리 (책임 기준)

```
frontend/   # 사용자 화면 · 마스코트 인터랙션   (스택·내부 구조 팀 자유)
backend/    # 수집 · 분류/요약 · API            (스택·내부 구조 팀 자유)
docs/       # 통합 계약 등 문서
.github/    # PR/이슈 템플릿
```

## 셋업 (개념 흐름 — 구체 명령은 각 디렉터리 README)

1. 로컬 인프라(DB/캐시 등) 기동
2. `backend/` 의존성 설치 후 실행
3. `frontend/` 의존성 설치 후 실행

각 단계의 도구·명령은 팀이 정해 `frontend/README.md`, `backend/README.md`에 기록합니다.

## 문서

- [기획 가이드라인](./hddb_guidelines.md)
- [통합 계약 (architecture)](./docs/architecture.md)
