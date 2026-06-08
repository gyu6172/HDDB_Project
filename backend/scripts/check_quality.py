import re
from app.core.database import SessionLocal
from app.models.article import Article
from app.models.category import *
from app.models.keyword import *

KOREAN_CHAR = re.compile(r'[가-힣]')
ERROR_PATTERNS = re.compile(r'(문단이 제공되지 않았습니다|문단을 제공해주시면|제공되지 않았습니다|알려주시면|요약해 드리겠습니다|죄송합니다)')

db = SessionLocal()
articles = db.query(Article).order_by(Article.title).all()

issues = {}

for a in articles:
    article_issues = []
    ps = a.paragraph_summary or []

    # original_content 짧음 (500자 미만)
    content_len = len(a.original_content or "")
    if content_len < 500:
        article_issues.append(f"[원문 짧음] {content_len}자")

    # one_line_summary 체크
    ols = a.one_line_summary or ""
    if not ols:
        article_issues.append("[one_line_summary 없음]")
    elif len(ols) < 10:
        article_issues.append(f"[one_line_summary 너무 짧음] {ols}")
    elif not KOREAN_CHAR.search(ols):
        article_issues.append(f"[one_line_summary 한글 없음] {ols[:50]}")

    # card_summary 체크
    cs = a.card_summary or ""
    if not cs:
        article_issues.append("[card_summary 없음]")
    elif len(cs) < 20:
        article_issues.append(f"[card_summary 너무 짧음] {cs}")
    elif not KOREAN_CHAR.search(cs):
        article_issues.append(f"[card_summary 한글 없음] {cs[:50]}")

    # paragraph_summary 없음
    if not ps:
        article_issues.append("[paragraph_summary 없음]")
    else:
        for p in ps:
            s = p.get("summary", "")
            idx = p.get("paragraph_index")
            if not s:
                article_issues.append(f"[문단{idx} 빈 요약]")
            elif ERROR_PATTERNS.search(s):
                article_issues.append(f"[문단{idx} 에러응답] {s[:40]}")
            elif len(s) < 8:
                article_issues.append(f"[문단{idx} 너무 짧음] '{s}'")
            elif not KOREAN_CHAR.search(s):
                article_issues.append(f"[문단{idx} 한글 없음] {s[:50]}")

    if article_issues:
        issues[a.id] = (a.title, article_issues)

db.close()

print(f"전체: {len(articles)}개 | 이슈 있는 기사: {len(issues)}개\n")
for aid, (title, issue_list) in issues.items():
    print(f"[{title[:65]}]")
    for iss in issue_list:
        print(f"  {iss}")
    print()
