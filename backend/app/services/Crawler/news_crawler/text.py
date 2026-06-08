"""HTML/텍스트 정리 유틸. crawler와 viewer가 공유."""
from __future__ import annotations

import html
import re

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"[ \t]+")
_BLANK_RE = re.compile(r"\n{3,}")


def strip_tags(text: str, *, replacement: str = " ") -> str:
    """HTML 태그만 제거. 분류기 프롬프트에 본문을 넣기 전 1차 정리용."""
    if not text:
        return ""
    return _TAG_RE.sub(replacement, text)


def clean_for_display(text: str) -> str:
    """사람이 읽기 좋게 정리: 태그 제거 + 엔티티 디코드 + 공백 정규화."""
    if not text:
        return ""
    text = _TAG_RE.sub("", text)
    text = html.unescape(text)
    text = _WS_RE.sub(" ", text)
    text = _BLANK_RE.sub("\n\n", text)
    return text.strip()
