import re
from app.core.database import SessionLocal
from app.models.article import Article
from app.models.category import *
from app.models.keyword import *

KOREAN_ENDINGS = re.compile(r"(에요|예요|답니다|랍니다|했어요|해요|있어요|없어요|이에요|거예요|거랍니다|됩니다|됐어요|겠어요|네요|군요|는군요|이군요|았어요|었어요|셨어요|아요|어요)")

db = SessionLocal()
articles = db.query(Article).order_by(Article.title).all()

no_summary = []
wrong_tone = []
ok = []

for a in articles:
    ps = a.paragraph_summary
    if not ps:
        no_summary.append(a)
        continue
    bad = [p for p in ps if p.get("summary") and not KOREAN_ENDINGS.search(p["summary"])]
    if bad:
        wrong_tone.append((a, bad))
    else:
        ok.append(a)

db.close()

print(f"전체: {len(articles)}개")
print(f"정상: {len(ok)}개")
print(f"paragraph_summary 없음: {len(no_summary)}개")
print(f"말투 불일치: {len(wrong_tone)}개")

print("\n=== paragraph_summary 없음 ===")
for a in no_summary:
    print(f"  {a.title[:70]}")

print("\n=== 말투 불일치 (문제 문단만) ===")
for a, bad_paras in wrong_tone:
    print(f"\n[{a.title[:60]}]")
    for p in bad_paras:
        print(f"  문단{p['paragraph_index']}: {p['summary']}")
