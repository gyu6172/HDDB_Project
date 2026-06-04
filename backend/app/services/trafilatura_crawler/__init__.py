"""trafilatura 기반 신규 크롤링 방식 (오프라인 테스트에서 검증).

기존 RSS 방식은 피드의 짧은 요약본(50~80자)만 본문으로 저장했으나,
이 방식은 RSS 를 '기사 URL 발견용' 으로만 쓰고 trafilatura 로 원문 페이지에서
전문(1,400~6,900자)을 추출한 뒤 보일러플레이트를 정제한다.

모듈:
- clean_paragraphs : trafilatura 추출 문단에서 소스별 정형 노이즈 제거
- dump_trafilatura : DB 의 original_url 로 trafilatura 전문 수집 + 정제
- collect_targeted : RSS 발견 → trafilatura 전문 → 정제 → 분류 (부족 카테고리 보충 수집)

주의: 이 파일들은 오프라인 테스트(summarize_offline) 기준으로 작성됐다.
HDDB 운영 통합 시 import 경로/분류기 경로/DB 세션 연결을 조정해야 한다(README 참고).
"""
