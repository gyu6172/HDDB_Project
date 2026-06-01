from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, model_validator


def _read_attr(data: Any, name: str) -> Any:
    if isinstance(data, dict):
        return data.get(name)
    return getattr(data, name, None)


def _relation_key(data: Any, relation_name: str) -> str | None:
    relation = _read_attr(data, relation_name)
    return _read_attr(relation, "key") if relation is not None else None


def _article_response_data(data: Any) -> Any:
    if isinstance(data, dict):
        return {
            **data,
            "category": data.get("category") or _relation_key(data, "category_rel"),
            "subcategory": data.get("subcategory") or _relation_key(data, "subcategory_rel"),
        }

    return {
        "id": _read_attr(data, "id"),
        "title": _read_attr(data, "title"),
        "one_line_summary": _read_attr(data, "one_line_summary"),
        "card_summary": _read_attr(data, "card_summary"),
        "source": _read_attr(data, "source"),
        "source_lang": _read_attr(data, "source_lang"),
        "published_at": _read_attr(data, "published_at"),
        "thumbnail_url": _read_attr(data, "thumbnail_url"),
        "category": _relation_key(data, "category_rel"),
        "subcategory": _relation_key(data, "subcategory_rel"),
        "confidence": _read_attr(data, "confidence"),
        "original_url": _read_attr(data, "original_url"),
        "content": _read_attr(data, "original_content"),
        "paragraph_summary": _read_attr(data, "paragraph_summary"),
    }


_ARTICLE_CARD_EXAMPLE = {
    "id": "3f1c9b7e-2a4d-4c0a-9b1e-8d2f6a5c1e90",
    "title": "부산항 컨테이너 물동량 사상 최대치 경신",
    "oneLineSummary": "부산항이 분기 컨테이너 물동량 신기록을 세웠다.",
    "cardSummary": "올해 1분기 부산항 컨테이너 물동량이 전년 대비 8% 증가하며 사상 최대치를 기록했다. 항만 당국은 환적 화물 증가를 주요 원인으로 분석했다.",
    "source": "BBC",
    "sourceLang": "en",
    "publishedAt": "2026-05-30T09:00:00",
    "thumbnailUrl": "https://example.com/thumbnails/3f1c9b7e.jpg",
    "category": "sea",
    "subcategory": "shipping",
    "confidence": 0.873,
}


class ParagraphSummary(BaseModel):
    """기사 본문 문단 단위 요약 항목 (ArticleDetail.paragraphSummaries 의 원소)."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "paragraphIndex": 0,
                "originalText": "Busan Port handled a record number of containers...",
                "summary": "부산항이 분기 기준 최대 컨테이너 물동량을 처리했다.",
            }
        },
    )

    paragraph_index: int = Field(serialization_alias="paragraphIndex")
    original_text:   str = Field(serialization_alias="originalText")
    summary:         str


class ArticleCard(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={"example": _ARTICLE_CARD_EXAMPLE},
    )

    id:               str
    title:            str
    one_line_summary: str | None = Field(serialization_alias="oneLineSummary")
    card_summary:     str | None = Field(serialization_alias="cardSummary")
    source:           str
    source_lang:      str = Field(serialization_alias="sourceLang")
    published_at:     datetime = Field(serialization_alias="publishedAt")
    thumbnail_url:    str | None = Field(serialization_alias="thumbnailUrl")
    category:         str
    subcategory:      str
    confidence:       float | None = None

    @model_validator(mode="before")
    @classmethod
    def flatten_category_relations(cls, data: Any) -> Any:
        return _article_response_data(data)


class SearchResultCard(ArticleCard):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={"example": {**_ARTICLE_CARD_EXAMPLE, "similarity": 0.91}},
    )

    similarity: float = Field(description="검색어와의 의미 유사도 (0~1, 높을수록 관련)")


class ArticleDetail(ArticleCard):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                **_ARTICLE_CARD_EXAMPLE,
                "originalUrl": "https://example.com/news/busan-port-record",
                "content": "Busan Port handled a record number of containers in the first quarter...",
                "paragraphSummaries": [ParagraphSummary.model_config["json_schema_extra"]["example"]],
            }
        },
    )

    original_url:      str = Field(serialization_alias="originalUrl")
    content:           str | None = None
    paragraph_summary: list[ParagraphSummary] | None = Field(
        default=None,
        serialization_alias="paragraphSummaries",
    )


class ArticleListResponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "items": [_ARTICLE_CARD_EXAMPLE],
                "nextCursor": "3f1c9b7e-2a4d-4c0a-9b1e-8d2f6a5c1e90",
            }
        },
    )

    items:       list[ArticleCard]
    next_cursor: str | None = Field(
        serialization_alias="nextCursor",
        description="다음 페이지 요청 시 cursor 로 전달할 마지막 항목의 id. null 이면 마지막 페이지.",
    )


class SearchResultResponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {"items": [{**_ARTICLE_CARD_EXAMPLE, "similarity": 0.91}]}
        },
    )

    items: list[SearchResultCard]
