from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    port: int = 8000
    gemini_api_key: str = ""
    enable_ai_pipeline: bool = True
    search_threshold: float = 0.5
    # 검색 시 반환할 유사도 상위 결과 개수. 프론트가 이 안에서 카테고리 필터/카운트/페이지네이션 처리.
    search_top_k: int = 100
    # 쉼표로 구분된 CORS 허용 origin 목록 (env 로 prod 도메인 추가 가능).
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
