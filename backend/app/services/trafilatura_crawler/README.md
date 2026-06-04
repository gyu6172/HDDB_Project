# trafilatura_crawler — 신규 크롤링 방식

기존 RSS 크롤러(`app/services/Crawler/news_crawler`)는 RSS 피드가 주는 **짧은 요약본
(50~80자)**을 본문으로 저장한다. 이 방식은 RSS 를 **기사 URL 발견용**으로만 쓰고,
실제 기사 페이지를 `trafilatura` 로 방문해 **본문 전문(1,400~6,900자)**을 추출한다.

## 파이프라인
```
RSS 피드 ──► URL 발견 ──► trafilatura 전문 추출 ──► clean_paragraphs 정제 ──► (분류/요약)
```

## 파일
| 파일 | 역할 |
|---|---|
| `clean_paragraphs.py` | trafilatura 추출 문단에서 소스별 정형 노이즈 제거(날짜·출처·인용·편집자 바이라인·개념태그 등). 본문 불릿은 라벨↔값 짝맞춤으로 보존 |
| `dump_trafilatura.py` | DB의 `original_url` 로 trafilatura 전문 수집 + 정제하여 JSON 덤프 |
| `collect_targeted.py` | RSS 발견 → trafilatura 전문 → 정제 → (로컬 LLM)분류. 부족 카테고리만 목표치까지 보충 수집 |

## 검증 결과(오프라인)
- RSS 대비 본문 길이 10~25배 증가
- 정제로 보일러플레이트 약 29% 문단 제거
- 100건 + 부족 카테고리 보충 39건 = 111건, 9개 카테고리 각 10건 이상 확보

## 운영 통합 시 조정 필요
이 파일들은 오프라인 테스트(`DB 기사 테스트용 파일/summarize_offline`) 기준으로 작성됨.
HDDB 운영에 통합하려면:
1. **import 경로**: `collect_targeted.py` 의 `clean_paragraphs`/`classify_articles` import,
   `DEFAULT_CLASSIFIER` 경로를 패키지 컨텍스트(`app.services...`)에 맞게 수정
2. **DB 세션**: `dump_trafilatura.py` 의 `SessionLocal` 을 `app.core.database` 로 연결
3. **분류기**: 기존 `app/services/Crawler/news_crawler/classifier.py` 재사용
   (기본 `qwen2.5:3b` 는 우주 분류 취약 → `qwen2.5:14b` 권장)
4. **의존성**: `pip install trafilatura` (requirements.txt 에 추가 필요)
5. 기존 `crawler.py` 의 `_pick_content`(RSS 본문) 를 trafilatura 추출로 대체하는 형태로
   연결하면 RSS→trafilatura 하이브리드가 된다.
"""
