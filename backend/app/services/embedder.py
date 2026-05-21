import google.generativeai as genai
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.keyword import ArticleKeyword

genai.configure(api_key=settings.gemini_api_key)

_MODEL = "models/text-embedding-004"


def embed_texts(texts: list[str]) -> list[list[float]]:
    return [
        genai.embed_content(model=_MODEL, content=text, task_type="retrieval_document")["embedding"]
        for text in texts
    ]


def embed_query(query: str) -> list[float]:
    return genai.embed_content(model=_MODEL, content=query, task_type="retrieval_query")["embedding"]


def embed_article(article_id: str, title: str, paragraph_summary: list | None, db: Session) -> None:
    texts = [title]
    if paragraph_summary:
        texts += [p["summary"] for p in paragraph_summary if p.get("summary")]

    vectors = embed_texts(texts)

    db.add_all([
        ArticleKeyword(article_id=article_id, text=text, embedding=vector)
        for text, vector in zip(texts, vectors)
    ])
    db.commit()
