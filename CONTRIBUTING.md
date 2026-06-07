# 기여 가이드

HDDB 프로젝트의 협업 규칙입니다. 작업 전 한 번 읽어주세요.

## 브랜치 전략

- 기준 브랜치는 **`develop`** 입니다. 모든 작업 브랜치는 `develop`에서 분기합니다.
- `main`은 배포/안정 브랜치이므로 직접 작업하지 않습니다.
- 작업 브랜치 이름은 **이슈 번호를 포함**합니다.

```
feat/#<이슈번호>-<짧은-설명>     # 기능 추가/개선
fix/#<이슈번호>-<짧은-설명>      # 버그 수정
```

예: `feat/#84-updateDocs`, `fix/#77-back-button`

## 이슈

- 작업은 **이슈 생성**으로 시작합니다.
- 템플릿을 사용하세요: `✨ 기능 제안`(enhancement) / `🐛 버그 리포트`(bug).
- 제목 규칙: 기능 `[Feat] <제목>`, 버그 `[Fix] <제목>`.

## 커밋 & PR

### 커밋/PR 제목

```
Task #<이슈번호>: [Feat|Fix] <설명>
```

예: `Task #81: [Fix] 검색 정렬 변경 시 히스토리 누적 방지`

### Pull Request

- 대상 브랜치는 **`develop`** 입니다.
- [PR 템플릿](.github/pull_request_template.md)을 채워주세요 — Summary / Issue Number / Tasks / To Reviewer / Screenshot.
- **Issue Number**에 관련 이슈를 연결합니다 (예: `> - #84`).
- 리뷰 승인 후 머지합니다.

## 개발 환경

- 백엔드: [`backend/README.md`](backend/README.md)
- 프론트엔드: [`frontend/README.md`](frontend/README.md)
- 통합 계약(API·enum·데이터): [`docs/architecture.md`](docs/architecture.md)
