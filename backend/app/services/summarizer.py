import json
import logging
import re

from google import genai
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.article import Article

logger = logging.getLogger(__name__)

_client = genai.Client(api_key=settings.gemini_api_key)
_DEFAULT_MODEL = "models/gemini-2.5-flash"

_PROMPT_TEMPLATE = """다음 뉴스 기사를 읽고 아래 JSON 형식으로 한국어 요약을 작성하세요.
영어 기사도 반드시 한국어로 요약하세요.

[말투]
- 초등학생도 이해할 수 있는 친근한 마스코트 말투로 작성하세요.
- 요약문은 자연스럽게 "~예요", "~한답니다", "~했어요" 같은 존댓말 어미를 사용하세요.
- 과장하거나 원문에 없는 내용을 덧붙이지 마세요.
- 전문 용어는 쉬운 말로 풀어 쓰되, 의미를 바꾸지 마세요.
- paragraph_summaries[].original_text는 원문 문단을 그대로 넣고 말투를 바꾸지 마세요.

[규칙]
- one_line_summary: 30~50자, 핵심 내용을 담은 한 문장
- card_summary: 100자 내외, 주요 내용 2~3문장
- paragraph_summaries: 각 문단을 30~50자로 요약. paragraph_index는 0부터 시작.

[출력 형식]
{{"one_line_summary": "...", "card_summary": "...", "paragraph_summaries": [{{"paragraph_index": 0, "original_text": "...", "summary": "..."}}]}}

[기사 제목]
{title}

[기사 본문]
{content}
"""


def _split_paragraphs(content: str) -> list[str]:
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [p.strip() for p in content.split("\n") if p.strip()]
    return paragraphs


def _parse_response(text: str) -> dict | None:
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip())
    cleaned = re.sub(r"\s*```$", "", cleaned)
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def summarize_article(article_id: str, db: Session, model: str = _DEFAULT_MODEL) -> list | None:
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article or not article.original_content:
        return None

    paragraphs = _split_paragraphs(article.original_content)
    content_snippet = "\n\n".join(paragraphs[:20])

    prompt = _PROMPT_TEMPLATE.format(title=article.title, content=content_snippet)

    try:
        response = _client.models.generate_content(model=model, contents=prompt)
        result = _parse_response(response.text)
    except Exception as e:
        if "RESOURCE_EXHAUSTED" in str(e) or "UNAVAILABLE" in str(e):
            raise  # 파이프라인이 처리
        logger.warning("Gemini 요약 실패: %s — %s", article.title[:60], e)
        return None

    if not result:
        logger.warning("Gemini 응답 파싱 실패: %s", article.title[:60])
        return None

    article.one_line_summary = result.get("one_line_summary")
    article.card_summary = result.get("card_summary")
    article.paragraph_summary = result.get("paragraph_summaries")
    db.commit()

    return article.paragraph_summary
