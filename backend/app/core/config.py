from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    port: int = 8000
    gemini_api_key: str = ""
    enable_ai_pipeline: bool = True
    search_threshold: float = 0.5
    # 쉼표로 구분된 CORS 허용 origin 목록 (env 로 prod 도메인 추가 가능).
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
