import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.article import Article
from app.models.category import *
from app.models.keyword import *

db = SessionLocal()
articles = db.query(Article).all()
short = [(len(a.original_content or ""), a) for a in articles if len(a.original_content or "") < 200]
db.close()

short.sort()
for length, a in short:
    content_preview = (a.original_content or "")[:150]
    print(f"[{length}자] {a.title}")
    print(f"  URL: {a.original_url}")
    print(f"  원문: {content_preview}")
    print()
