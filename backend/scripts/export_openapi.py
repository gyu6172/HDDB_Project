"""OpenAPI 스펙(openapi.json)을 파일로 추출한다.

프론트 담당자에게 전달하거나 TS 타입 자동 생성(openapi-typescript 등)에 사용한다.
DB 연결 없이 동작하도록 앱의 OpenAPI 스키마만 생성한다.

사용:
    python -m scripts.export_openapi              # backend/openapi.json 으로 저장
    python -m scripts.export_openapi out.json     # 경로 지정
"""
import json
import sys
from pathlib import Path

from app.main import app


def main() -> None:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "openapi.json"
    spec = app.openapi()
    out.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OpenAPI 스펙을 저장했습니다: {out}")


if __name__ == "__main__":
    main()
