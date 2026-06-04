import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.article import Article
from app.models.category import *
from app.models.keyword import *

KOREAN_CHAR = re.compile(r'[가-힣]')
ERROR_PATTERNS = re.compile(r'(문단이 제공되지 않았습니다|문단을 제공해주시면|제공되지 않았습니다|알려주시면|요약해 드리겠습니다|죄송합니다)')
# 기관/출처 나열형: 의미 없는 메타 문장
META_PATTERNS = re.compile(r'(대학이 참여했습니다|연구소가 참여했습니다|연구비는|지원을 받았습니다|저널에 발표되었습니다|논문 제목은|연구진은 여러 나라|공개되어 다른 연구진|연구 결과는 공개)')

db = SessionLocal()
articles = db.query(Article).order_by(Article.title).all()

issues = {}

for a in articles:
    ps = a.paragraph_summary or []
    article_issues = []

    for p in ps:
        s = p.get("summary", "") or ""
        idx = p.get("paragraph_index")

        if not s:
            article_issues.append(f"문단{idx}: [빈 요약]")
        elif ERROR_PATTERNS.search(s):
            article_issues.append(f"문단{idx}: [에러응답] {s[:50]}")
        elif len(s) < 8:
            article_issues.append(f"문단{idx}: [너무 짧음] '{s}'")
        elif not KOREAN_CHAR.search(s):
            article_issues.append(f"문단{idx}: [한글 없음] {s[:50]}")
        elif META_PATTERNS.search(s):
            article_issues.append(f"문단{idx}: [메타/기관나열] {s[:60]}")

    if article_issues:
        issues[a.id] = (a.title, article_issues)

db.close()

print(f"전체: {len(articles)}개 | 이슈 있는 기사: {len(issues)}개\n")
for aid, (title, issue_list) in issues.items():
    print(f"[{title[:65]}]")
    for iss in issue_list:
        print(f"  {iss}")
    print()
