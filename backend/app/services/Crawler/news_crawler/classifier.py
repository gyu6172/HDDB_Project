"""Ollama 로컬 LLM으로 뉴스 기사를 사전 정의된 자연 카테고리에 다중 분류한다.

- 자연(하늘/땅/바다)과 무관한 기사는 빈 리스트를 반환 → 호출자가 저장에서 제외.
- 결과는 카테고리 slug 리스트 (예: ["marine_life", "disaster"]).
- 호출 전에 키워드 사전 필터(`passes_prefilter`)로 명백히 무관한 기사는 LLM 호출 없이 제외.

요구사항:
- Ollama 가 로컬에서 실행 중이어야 함 (`ollama serve`, 보통 http://localhost:11434).
- 사용할 모델이 미리 pull 되어 있어야 함 (예: `ollama pull qwen2.5:3b`).
"""
from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

import requests

logger = logging.getLogger(__name__)


# (group, slug, label_ko, 설명) — 프롬프트와 시드에 동시에 사용.
CATEGORY_DEFS: list[tuple[str, str, str, str]] = [
    ("sky", "bird", "조류", "야생 새, 철새, 멸종위기 조류, 조류 생태"),
    ("sky", "space", "우주", "우주 탐사, 천문, 별/행성/은하, 위성, 로켓"),
    ("sky", "weather", "기상", "날씨, 기후, 태풍, 폭염, 한파, 강수, 기후변화"),
    ("land", "disaster", "재난", "지진, 산불, 홍수, 산사태, 화산 등 자연재해 사건"),
    ("land", "animal", "동물", "육상 야생/가축 동물, 멸종위기 종, 생태계"),
    ("land", "ground_pollution", "토양오염", "토양/지하수 오염, 폐기물, 농지 오염, 미세플라스틱(육상)"),
    ("sea", "marine_life", "해양생물", "어류, 해양 포유류, 산호, 해조류 등 바다 생물"),
    ("sea", "deep_sea", "심해", "심해 탐사, 심해 생태, 해저 지형, 해저 자원"),
    ("sea", "ocean_pollution", "해양오염", "해양 플라스틱, 기름유출, 적조, 해양 폐기물"),
]

VALID_SLUGS = {slug for _, slug, _, _ in CATEGORY_DEFS}


# 분명히 자연 관련 아닌 기사를 LLM 호출 전에 걸러내기 위한 키워드.
# 제목 또는 본문에 이 단어가 하나도 없으면 즉시 제외.
# 매칭은 대소문자 무시 + 단순 부분문자열 (정밀도보다 재현율 우선).
PREFILTER_KEYWORDS: tuple[str, ...] = (
    # --- 하늘 ---
    "조류", "새", "철새", "텃새", "멸종위기", "야생동물",
    "우주", "천체", "행성", "별", "은하", "위성", "로켓", "탐사선", "블랙홀",
    "유성", "혜성", "달", "화성", "목성", "토성", "태양",
    "기상", "날씨", "기후", "온난화", "이상기후", "폭염", "한파", "장마",
    "태풍", "허리케인", "강수", "가뭄", "황사", "미세먼지",
    "bird", "birds", "avian", "migratory",
    "space", "cosmos", "cosmic", "astronomy", "astronomical", "planet",
    "galaxy", "satellite", "rocket", "nasa", "spacex", "mars", "lunar",
    "moon", "solar", "asteroid", "comet", "telescope", "orbit",
    "weather", "climate", "warming", "temperature", "storm", "hurricane",
    "typhoon", "drought", "heatwave", "rainfall", "snowfall", "wildfire",
    # --- 땅 ---
    "지진", "산불", "홍수", "산사태", "화산", "재난", "재해", "쓰나미",
    "동물", "포유류", "파충류", "곤충", "야생",
    "토양", "오염", "폐기물", "쓰레기", "플라스틱", "농지", "벌목", "삼림", "사막화",
    "earthquake", "wildfire", "flood", "landslide", "volcano", "volcanic",
    "disaster", "tsunami", "drought",
    "animal", "animals", "wildlife", "mammal", "reptile", "insect",
    "endangered", "species", "biodiversity", "extinction",
    "soil", "pollution", "waste", "plastic", "deforestation", "desert",
    "forest", "ecosystem",
    # --- 바다 ---
    "바다", "해양", "해안", "해변", "어류", "물고기", "고래", "돌고래",
    "산호", "해조", "어업", "양식", "심해", "해저", "조개", "갑각류",
    "기름유출", "적조", "해양쓰레기",
    "ocean", "sea", "marine", "coast", "coastal", "beach",
    "fish", "whale", "dolphin", "shark", "coral", "reef", "algae",
    "fishery", "fishing", "deep-sea", "seabed", "seafloor",
    "oil spill", "red tide",
    # --- 일반 ---
    "환경", "생태", "생물", "자연",
    "environment", "ecology", "biology", "nature", "conservation",
)


def passes_prefilter(title: str, content: str) -> bool:
    """제목+본문에 자연 관련 키워드가 하나라도 있으면 True."""
    haystack = f"{title}\n{content}".lower()
    return any(kw.lower() in haystack for kw in PREFILTER_KEYWORDS)


def _build_prompt(title: str, content: str) -> str:
    catalog_lines = [
        f'- "{slug}" ({group}/{label}): {desc}'
        for group, slug, label, desc in CATEGORY_DEFS
    ]
    catalog = "\n".join(catalog_lines)

    snippet = (content or "")[:1500]

    return f"""당신은 뉴스 기사 분류기입니다. 아래 기사를 읽고, 자연 관련 카테고리 중 해당되는 것을 모두 선택하세요.

[카테고리 목록]
{catalog}

[분류 규칙]
1. 자연(하늘/땅/바다)과 무관한 기사(정치, 경제, 연예, 스포츠, 일반 사회 등)이면 빈 배열을 반환.
2. 해당되는 카테고리가 있으면 그 slug들을 배열로 반환. 여러 개 가능.
   예: 해양 동물 관련 재난이면 ["marine_life", "disaster"].
3. 추측하지 말고 기사 내용에 명확히 근거가 있을 때만 분류.
4. 반드시 다음 JSON 형식으로만 응답하세요. 다른 텍스트 금지.

[출력 형식]
{{"categories": ["slug1", "slug2"]}}

[기사 제목]
{title}

[기사 본문]
{snippet}
"""


def _parse_response(text: str) -> list[str]:
    """LLM 응답에서 categories 배열을 추출. 형식 어긋나면 빈 리스트."""
    if not text:
        return []

    cleaned = text.strip()
    # 코드펜스(```json ... ```) 제거.
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    # 본문 안에 JSON 객체가 있을 수 있으니 첫 { ... } 만 추출.
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        return []
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return []

    cats = data.get("categories") if isinstance(data, dict) else None
    if not isinstance(cats, list):
        return []

    result: list[str] = []
    seen: set[str] = set()
    for c in cats:
        if not isinstance(c, str):
            continue
        slug = c.strip().lower()
        if slug in VALID_SLUGS and slug not in seen:
            result.append(slug)
            seen.add(slug)
    return result


class OllamaUnavailable(RuntimeError):
    """Ollama 서버에 접속할 수 없거나 모델이 준비되지 않음."""


class OllamaClassifier:
    """로컬 Ollama 서버를 통한 분류기.

    환경변수:
    - OLLAMA_HOST: Ollama 서버 주소 (기본 http://localhost:11434)
    - OLLAMA_MODEL: 사용할 모델 이름 (기본 qwen2.5:3b)
    - OLLAMA_TIMEOUT: 요청 타임아웃 초 (기본 120)
    """

    def __init__(
        self,
        host: str | None = None,
        model: str | None = None,
        timeout: int | None = None,
    ) -> None:
        self._host = (host or os.getenv("OLLAMA_HOST", "http://localhost:11434")).rstrip("/")
        self._model = model or os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
        self._timeout = timeout or int(os.getenv("OLLAMA_TIMEOUT", "120"))
        self._call_count = 0
        self._verify_ready()

    @property
    def call_count(self) -> int:
        return self._call_count

    @property
    def model_name(self) -> str:
        return self._model

    def _verify_ready(self) -> None:
        """서버 도달 가능 + 모델 존재 여부 확인. 실패 시 OllamaUnavailable."""
        try:
            r = requests.get(f"{self._host}/api/tags", timeout=5)
            r.raise_for_status()
        except requests.RequestException as exc:
            raise OllamaUnavailable(
                f"Ollama 서버에 접속 실패 ({self._host}). "
                "터미널에서 `ollama serve` 를 먼저 실행하세요."
            ) from exc

        installed = {m.get("name", "") for m in r.json().get("models", [])}
        # 모델 이름은 ':latest' 가 붙은 형태로 저장될 수 있으니 prefix 매칭도 허용.
        base = self._model.split(":")[0]
        if not any(
            name == self._model
            or name.startswith(f"{self._model}:")
            or name.startswith(f"{base}:")
            for name in installed
        ):
            raise OllamaUnavailable(
                f"모델 '{self._model}' 이(가) 설치돼 있지 않습니다. "
                f"먼저 `ollama pull {self._model}` 을 실행하세요. "
                f"설치된 모델: {sorted(installed) or '(없음)'}"
            )

    def classify(self, title: str, content: str) -> list[str]:
        """제목+본문 → 해당 카테고리 slug 리스트. 무관 기사면 []."""
        prompt = _build_prompt(title, content)
        payload: dict[str, Any] = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
            "format": "json",  # Ollama 가 응답을 valid JSON 으로 강제
            "options": {
                "temperature": 0.0,  # 분류는 결정론적으로
                "num_predict": 256,  # 응답은 짧으면 충분
            },
        }

        self._call_count += 1
        try:
            r = requests.post(
                f"{self._host}/api/generate",
                json=payload,
                timeout=self._timeout,
            )
            r.raise_for_status()
        except requests.RequestException as exc:
            logger.warning("Ollama 호출 실패: %s", str(exc)[:200])
            return []

        try:
            data = r.json()
        except ValueError:
            logger.warning("Ollama 응답 JSON 파싱 실패")
            return []

        text = data.get("response") or ""
        return _parse_response(text)
