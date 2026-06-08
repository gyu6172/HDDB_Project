from pydantic import BaseModel, ConfigDict, Field


class ErrorResponse(BaseModel):
    """공통 에러 응답.

    FastAPI 의 ``HTTPException(detail=...)`` 및 검증 실패(422) 응답과 동일한 형태.
    프론트는 비정상 응답(4xx/5xx)에서 항상 이 형태를 기대하면 된다.
    """

    model_config = ConfigDict(
        json_schema_extra={"example": {"detail": "Article not found"}}
    )

    detail: str = Field(description="사람이 읽을 수 있는 에러 메시지")
