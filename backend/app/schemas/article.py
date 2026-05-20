from datetime import datetime
from typing import Any
from pydantic import BaseModel


class ArticleCard(BaseModel):
    id:              str
    title:           str
    one_line_summary: str | None
    card_summary:    str | None
    source:          str
    source_lang:     str
    published_at:    datetime
    thumbnail_url:   str | None
    category:        str
    subcategory:     str

    class Config:
        from_attributes = True


class ArticleDetail(ArticleCard):
    original_url:      str
    original_content:  str | None
    paragraph_summary: list[Any] | None


class ArticleListResponse(BaseModel):
    items:       list[ArticleCard]
    next_cursor: str | None
