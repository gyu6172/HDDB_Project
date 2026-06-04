import re
from app.core.database import SessionLocal
from app.models.article import Article
from app.models.category import *
from app.models.keyword import *

ERROR_PATTERNS = re.compile(
    r"(문단이 제공되지 않았습니다|문단을 제공해주시면|제공되지 않았습니다|알려주시면|요약해 드리겠습니다|죄송합니다)"
)

db = SessionLocal()
articles = db.query(Article).order_by(Article.title).all()

bad_articles = []
for a in articles:
    ps = a.paragraph_summary or []
    bad_paras = [p for p in ps if p.get("summary") and ERROR_PATTERNS.search(p["summary"])]
    if bad_paras:
        bad_articles.append((a, bad_paras))

db.close()

print(f"에러 응답 문단 포함 기사: {len(bad_articles)}개\n")
for a, bad_paras in bad_articles:
    print(f"[{a.title[:60]}]")
    for p in bad_paras:
        print(f"  문단{p['paragraph_index']}: {p['summary']}")
    print()
