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
from dataclasses import dataclass
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


@dataclass(frozen=True)
class ClassificationResult:
    """분류 결과: 가장 적합한 단일 카테고리와 확신도(0.0~1.0).

    - slug 가 None 이면 자연 카테고리에 해당하지 않는 기사 → 저장 대상 아님.
    - confidence 는 항상 0.0~1.0 범위. slug 가 None 이면 0.0.
    """

    slug: str | None
    confidence: float

    @property
    def matched(self) -> bool:
        return self.slug is not None


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
    "typhoon", "drought", "heatwave", "rainfall", "snowfall",
    # --- 땅 ---
    "지진", "산불", "홍수", "산사태", "화산", "재난", "재해", "쓰나미",
    "동물", "포유류", "파충류", "곤충", "야생",
    "토양", "오염", "폐기물", "쓰레기", "플라스틱", "농지", "벌목", "삼림", "사막화",
    "earthquake", "wildfire", "flood", "landslide", "volcano", "volcanic",
    "disaster", "tsunami",
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

    return f"""당신은 뉴스 기사 분류기입니다. 아래 기사를 읽고, 자연 관련 카테고리 중 "가장 적합한" 단 한 개를
선택하고, 그 분류에 대한 확신도(confidence)를 0.0~1.0 사이 값으로 함께 매기세요.

[카테고리 목록]
{catalog}

[분류 규칙]
1. 자연(하늘/땅/바다)과 무관한 기사(정치, 경제, 연예, 스포츠, 일반 사회 등)이면
   "category": null, "confidence": 0.0 을 반환.
2. 해당되는 카테고리가 있으면 가장 잘 맞는 slug 한 개만 선택. 여러 개 분류 금지.
   주제가 두 영역에 걸치면 기사의 "주된 초점" 에 해당하는 한 개를 골라라.
3. 추측하지 말고 기사 내용에 명확히 근거가 있을 때만 분류.
4. confidence 는 다음 기준을 따른다:
   - 0.90~1.00: 제목/본문에 명시적 근거가 있고, 다른 카테고리와 혼동의 여지가 거의 없음.
   - 0.70~0.89: 본문 다수가 해당 주제이지만 다른 자연 카테고리와도 일부 겹침.
   - 0.50~0.69: 해당 카테고리일 가능성이 가장 높지만 모호함이 남음.
   - 0.50 미만: 확신이 낮다. 이 경우 차라리 category=null 을 선택하라.
5. 반드시 다음 JSON 형식으로만 응답하세요. 다른 텍스트 금지.

[카테고리 구분 규칙 — 자주 헷갈리는 케이스]
A) 해양 생물 vs 육상 동물
   - 고래/돌고래/상어/물고기/바다거북/물범/펭귄/산호 등 바다에서 사는 생물은 반드시
     "marine_life" 로 분류한다. 절대 "animal" 로 분류하지 말 것.
   - "animal" 은 육상 야생/가축 동물 전용 (사자, 코끼리, 사슴, 곰, 새는 "bird" 등).
B) 심해 vs 그 외
   - "deep_sea" 는 (a) 심해/해저 탐사, (b) 심해 생물 발견, (c) 해저 지형/지질,
     (d) 해저 자원·열수공 등 "수심이 깊은 바다 환경 자체" 를 다루는 기사에만 사용.
   - 지진·해일·빙하 붕괴는 바다에서 일어나더라도 "deep_sea" 가 아니라 "disaster".
   - 해수면 상승·해양 순환 변화·바다 온도 변화는 "deep_sea" 가 아니라 "weather"
     (또는 해양 생태계가 주된 초점이면 "marine_life"/"ocean_pollution").
   - 과거 지질사·산맥 형성처럼 "오래전 바다였다" 류 기사는 자연 카테고리 없음 → null.
C) 해양 오염 vs 토양 오염
   - 기름유출/해양 플라스틱/적조/해양 쓰레기 → "ocean_pollution".
   - PFAS·중금속이 해안에서 발견되어도 "바다 환경 오염" 맥락이면 "ocean_pollution",
     육상 폐기물·농지 오염이 주제면 "ground_pollution".
D) 우주(space) 사용 제한
   - 천문/위성/로켓/행성 등 우주 자체가 주제일 때만 "space".
   - NASA 가 등장해도 지구·해양·기후를 관측한 기사면 "weather"/"ocean_pollution"/"marine_life" 등
     해당 주제로 분류하고 "space" 는 쓰지 말 것.
E) "sea wall(방조제)·연안 인프라·해수면 상승" 같이 바다가 주제인 기사는 적어도 하나의
   sea 그룹 카테고리(marine_life / deep_sea / ocean_pollution) 또는 weather/disaster
   중 적합한 것을 골라야 한다. 명백히 자연 기사인데 null 을 반환하지 말 것.

[예시]
- 제목: "Humpback whale breaks migration record with 15,000 km ocean journey"
  → {{"category": "marine_life", "confidence": 0.95}}   ("animal" 아님)
- 제목: "Scientists discover hidden brakes that stop massive earthquakes"
  → {{"category": "disaster", "confidence": 0.92}}      ("deep_sea" 아님)
- 제목: "Antarctic glacier collapses at record speed"
  → {{"category": "disaster", "confidence": 0.80}}   (weather 도 가능하지만 사건성이 주된 초점)
- 제목: "Giant squid discovery uncovers a hidden deep-sea world off Australia"
  → {{"category": "deep_sea", "confidence": 0.88}}   (심해 환경이 주된 초점, marine_life 도 가능)
- 제목: "High levels of toxic 'forever chemicals' found off coast of southern England"
  → {{"category": "ocean_pollution", "confidence": 0.93}}
- 제목: "NASA captures wild swirling clouds and rare arctic storm over Alaska"
  → {{"category": "weather", "confidence": 0.90}}       ("space" 아님)
- 제목: "Stock market hits record high amid earnings season"
  → {{"category": null, "confidence": 0.0}}

[출력 형식]
{{"category": "slug 또는 null", "confidence": 0.0~1.0}}

[기사 제목]
{title}

[기사 본문]
{snippet}
"""


_EMPTY_RESULT = ClassificationResult(slug=None, confidence=0.0)


def _coerce_confidence(value: Any) -> float:
    """confidence 값을 0.0~1.0 float 로 정규화. 잘못된 값은 0.0."""
    try:
        c = float(value)
    except (TypeError, ValueError):
        return 0.0
    if c != c:  # NaN
        return 0.0
    if c < 0.0:
        return 0.0
    if c > 1.0:
        # 모델이 0~100 으로 답한 경우 등 흔한 실수 보정.
        if c <= 100.0:
            return min(1.0, c / 100.0)
        return 1.0
    return c


def _parse_response(text: str) -> ClassificationResult:
    """LLM 응답에서 (category, confidence) 를 추출. 형식 어긋나면 빈 결과.

    하위 호환: 과거 형식 {"categories": [...]} 가 와도 첫 유효 슬러그를
    채택하고 confidence 는 0.5 로 둔다.
    """
    if not text:
        return _EMPTY_RESULT

    cleaned = text.strip()
    # 코드펜스(```json ... ```) 제거.
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    # 본문 안에 JSON 객체가 있을 수 있으니 첫 { ... } 만 추출.
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        return _EMPTY_RESULT
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return _EMPTY_RESULT
    if not isinstance(data, dict):
        return _EMPTY_RESULT

    # --- 신규 형식: {"category": "...", "confidence": 0.x} ---
    if "category" in data:
        raw_slug = data.get("category")
        if raw_slug is None:
            return _EMPTY_RESULT
        if not isinstance(raw_slug, str):
            return _EMPTY_RESULT
        slug = raw_slug.strip().lower()
        if slug not in VALID_SLUGS:
            return _EMPTY_RESULT
        confidence = _coerce_confidence(data.get("confidence", 0.0))
        return ClassificationResult(slug=slug, confidence=confidence)

    # --- 하위 호환: {"categories": [...]} 형식 ---
    cats = data.get("categories")
    if isinstance(cats, list):
        for c in cats:
            if not isinstance(c, str):
                continue
            slug = c.strip().lower()
            if slug in VALID_SLUGS:
                return ClassificationResult(slug=slug, confidence=0.5)

    return _EMPTY_RESULT


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

    def classify(self, title: str, content: str) -> ClassificationResult:
        """제목+본문 → 가장 적합한 단일 카테고리 + confidence.

        자연 카테고리와 무관하거나 모델 응답이 비정상이면
        ClassificationResult(slug=None, confidence=0.0) 을 반환한다.
        """
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
            return _EMPTY_RESULT

        try:
            data = r.json()
        except ValueError:
            logger.warning("Ollama 응답 JSON 파싱 실패")
            return _EMPTY_RESULT

        text = data.get("response") or ""
        return _parse_response(text)
