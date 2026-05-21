from google import genai
from google.genai import types
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.keyword import ArticleKeyword

_client = genai.Client(api_key=settings.gemini_api_key)
_MODEL = "text-embedding-004"


def embed_texts(texts: list[str]) -> list[list[float]]:
    return [
        list(_client.models.embed_content(
            model=_MODEL,
            contents=text,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
        ).embeddings[0].values)
        for text in texts
    ]


def embed_query(query: str) -> list[float]:
    return list(_client.models.embed_content(
        model=_MODEL,
        contents=query,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    ).embeddings[0].values)


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
