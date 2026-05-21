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


class ArticleCard(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

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


class ArticleDetail(ArticleCard):
    original_url:      str = Field(serialization_alias="originalUrl")
    content:           str | None = None
    paragraph_summary: list[Any] | None = Field(
        default=None,
        serialization_alias="paragraphSummaries",
    )


class ArticleListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items:       list[ArticleCard]
    next_cursor: str | None = Field(serialization_alias="nextCursor")
