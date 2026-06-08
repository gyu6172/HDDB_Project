"""trafilatura 덤프 JSON의 paragraphs 에서 본문이 아닌 보일러플레이트를 제거한다.

100건 분석으로 파악한 소스별 정형 노이즈를 규칙으로 제거한다:
  - 제목 중복(첫 문단 == title)
  - ScienceDaily 메타블록: "- Date:/- Source:/- Summary:/- Share:" + 값,
                           footer "Story Source:/Journal Reference:/Cite This Page:" 등
  - Phys.org 편집자 바이라인(이름 + "Scientific Editor" 류), "Publication details" 등
  - BBC 푸터("Follow BBC ..."), 팟캐스트 마커("Episode details" 등)
  - 공통 출처/인용 라인("Materials provided by ...", "Provided by ...", "Journal information:")

본문 안의 진짜 불릿(예: Phys.org "- Tropical cyclones cause ...")은 보존하기 위해
'- ' 라인을 일괄 삭제하지 않고, 라벨+값 짝맞추기 방식으로 제거한다.

실행:
  python summarize_offline/clean_paragraphs.py \
      --in summarize_offline/articles_dump_trafilatura_100.json \
      --out summarize_offline/articles_dump_trafilatura_100.cleaned.json
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import unicodedata

# --- 단독으로 등장하면 노이즈인 라벨/마커 (소문자 비교) ---
EXACT_NOISE = {
    "- share:",
    "story source:",
    "cite this page:",
    "key concepts",
    "scientific editor",
    "lead editor",
    "associate editor",
    "managing editor",
    "editor",
    "episode details",
    "programme website",
    "advertisement",
    "- the conversation",
}

# --- 라벨 다음 줄이 '값'이라 라벨+값을 함께 제거 ---
LABEL_WITH_VALUE = {
    "- date:",
    "- source:",
    "- summary:",
    "publication details",
    "more information",
}

# --- 라벨 + 뒤따르는 "- ..." 인용 라인을 모두 제거 (footer 전용) ---
CITATION_LABELS = {
    "journal reference:",
    "journal references:",
}

# --- 이 접두어로 시작하면 노이즈 ---
PREFIX_NOISE = (
    "materials provided by",
    "provided by ",
    "journal information:",
    "follow bbc",
    "sign up to",
    "this article was",
    "story source:",
    "read more",
)

# "EnvironmentProvided by University of Arkansas" 처럼 태그에 붙은 출처
GLUED_PROVIDED_RE = re.compile(r"[a-z]Provided by ")
# 캐멀케이스로 뭉친 개념 태그 묶음(Phys.org "Key concepts" 값) 감지용
CAMEL_RE = re.compile(r"[a-z][A-Z]")

EDITOR_TITLES = {
    "scientific editor",
    "lead editor",
    "associate editor",
    "managing editor",
    "editor",
}

# "- April 25, 2026" / "- May 4, 2026" 같은 날짜 라인
DATE_RE = re.compile(
    r"^-?\s*(january|february|march|april|may|june|july|august|"
    r"september|october|november|december)\s+\d{1,2},?\s+\d{4}\.?$",
    re.IGNORECASE,
)
# "Available for 12 days"
AVAILABLE_RE = re.compile(r"^available for\s+\d+\s+days?$", re.IGNORECASE)


def _norm(s: str) -> str:
    """비교용 정규화: 양끝 공백 제거 + 스마트따옴표 통일 + 소문자."""
    s = unicodedata.normalize("NFKC", s).strip()
    s = s.replace("’", "'").replace("‘", "'")
    s = s.replace("“", '"').replace("”", '"')
    return s


def _is_tag_soup(p: str) -> bool:
    """캐멀케이스로 단어가 뭉친 개념 태그 묶음인가(문장이 아님)."""
    s = p.strip()
    if not s or len(s) < 20 or s.endswith((".", "?", "!")):
        return False
    return len(CAMEL_RE.findall(s)) >= 2


def _is_name_like(p: str) -> bool:
    """편집자 이름처럼 보이는가(짧고, 마침표 없고, 제목대소문자)."""
    s = p.strip()
    if not s or s.endswith((".", ":", "?", "!")):
        return False
    words = s.split()
    if not (1 <= len(words) <= 3):
        return False
    return all(re.match(r"^[A-Z][a-zA-Z.'-]*$", w) for w in words)


def clean_paragraphs(title: str, paras: list[str]) -> tuple[list[str], list[str]]:
    """(정제된 문단, 제거된 문단) 반환."""
    title_n = _norm(title)
    n = len(paras)
    remove = [False] * n

    i = 0
    while i < n:
        p = paras[i]
        pn = _norm(p)
        low = pn.lower()

        # 1) 제목 중복(보통 첫 문단)
        if pn == title_n:
            remove[i] = True
            i += 1
            continue

        # 2) 인용 라벨 + 뒤따르는 "- ..." 인용 라인 전부 제거 (footer)
        if low in CITATION_LABELS:
            remove[i] = True
            i += 1
            while i < n and _norm(paras[i]).startswith("-"):
                remove[i] = True
                i += 1
            continue

        # 3) 라벨+값 짝제거
        if low in LABEL_WITH_VALUE:
            remove[i] = True
            if i + 1 < n:
                remove[i + 1] = True
                i += 2
            else:
                i += 1
            continue

        # 4) 단독 라벨/마커, 접두어, 날짜, 방송시간, 태그묶음
        if (
            low in EXACT_NOISE
            or low.startswith(PREFIX_NOISE)
            or DATE_RE.match(pn)
            or AVAILABLE_RE.match(pn)
            or GLUED_PROVIDED_RE.search(pn)
            or _is_tag_soup(pn)
        ):
            remove[i] = True
            i += 1
            continue

        i += 1

    # 4) 편집자 직함 앞의 '이름' 라인 제거 (Phys.org 바이라인)
    for idx in range(n):
        if _norm(paras[idx]).lower() in EDITOR_TITLES and remove[idx]:
            j = idx - 1
            # 바로 앞의 (아직 살아있는) 라인이 이름처럼 보이면 제거
            while j >= 0 and remove[j]:
                j -= 1
            if j >= 0 and _is_name_like(paras[j]):
                remove[j] = True

    kept = [p for k, p in enumerate(paras) if not remove[k]]
    dropped = [p for k, p in enumerate(paras) if remove[k]]
    return kept, dropped


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp",
                    default="summarize_offline/articles_dump_trafilatura_100.json")
    ap.add_argument("--out",
                    default="summarize_offline/articles_dump_trafilatura_100.cleaned.json")
    ap.add_argument("--show", type=int, default=25,
                    help="가장 많이 제거된 라인 상위 N개 출력")
    args = ap.parse_args()

    with open(args.inp, encoding="utf-8") as f:
        data = json.load(f)

    total_before = total_after = 0
    dropped_counter: collections.Counter[str] = collections.Counter()
    per_source = collections.defaultdict(lambda: [0, 0])  # source -> [before, after]
    articles_touched = 0

    for d in data:
        paras = d.get("paragraphs") or []
        before = len(paras)
        kept, dropped = clean_paragraphs(d.get("title", ""), paras)
        d["paragraphs"] = kept
        d["new_content_len"] = sum(len(p) for p in kept)

        after = len(kept)
        total_before += before
        total_after += after
        if dropped:
            articles_touched += 1
        for p in dropped:
            dropped_counter[_norm(p)[:60]] += 1
        src = d.get("source", "?")
        per_source[src][0] += before
        per_source[src][1] += after

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    removed = total_before - total_after
    pct = removed / total_before * 100 if total_before else 0
    print("=" * 60)
    print(f"기사 수            : {len(data)}건 (정제 발생 {articles_touched}건)")
    print(f"전체 문단 (정제 전) : {total_before}")
    print(f"전체 문단 (정제 후) : {total_after}")
    print(f"제거된 문단        : {removed}  ({pct:.1f}%)")
    print(f"저장               : {args.out}")
    print("=" * 60)

    print("\n[소스별 문단 수 변화]")
    print(f"{'SOURCE':40s} {'BEFORE':>7} {'AFTER':>7} {'DROP':>6}")
    print("-" * 64)
    for src, (b, a) in sorted(per_source.items(), key=lambda x: x[1][0] - x[1][1], reverse=True):
        print(f"{src[:40]:40s} {b:7d} {a:7d} {b - a:6d}")

    print(f"\n[가장 많이 제거된 라인 상위 {args.show}개]")
    for line, cnt in dropped_counter.most_common(args.show):
        print(f"{cnt:4d} | {line}")


if __name__ == "__main__":
    main()
