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

### 릴리스 브랜치 · 태그

배포는 GitFlow 릴리스 흐름을 따릅니다. `v1.0.0` 릴리스가 이 절차로 진행되었습니다.

1. `develop`에서 `release/<버전>` 브랜치를 분기합니다. (예: `release/v1.0.0`)
2. 릴리스 브랜치에서는 **배포 설정·버전 고정·최종 점검**만 수행합니다. 기능 추가는 하지 않고 마무리 수정만 합니다.
3. 완료되면 `main`에 병합하고, 그 커밋에 **버전 태그**를 답니다.
4. 릴리스 내용을 `develop`에도 다시 반영(back-merge)해 누락을 막습니다.

**버전 태그**는 [Semantic Versioning](https://semver.org/lang/ko/)을 따릅니다 — `v<MAJOR>.<MINOR>.<PATCH>` (예: `v1.0.0`).

- **MAJOR**: 호환되지 않는 변경 · **MINOR**: 호환되는 기능 추가 · **PATCH**: 호환되는 버그 수정

```bash
git checkout main && git pull
git tag -a v1.0.0 -m "v1.0.0"
git push origin v1.0.0
```

### 핫픽스 브랜치

> 배포된 `main`에서 긴급 버그가 발생할 경우를 대비한 규약입니다. (v1.0.0 시점까지 사용 사례는 없습니다.)

- `main`에서 `hotfix/#<이슈번호>-<설명>` 브랜치를 분기 → 수정 → **`main`과 `develop` 양쪽에 병합**합니다.
- `main` 병합 커밋에는 PATCH 버전 태그를 답니다. (예: `v1.0.1`)

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
