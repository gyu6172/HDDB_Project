from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    port: int = 8000
    gemini_api_key: str = ""
    enable_ai_pipeline: bool = True
    search_threshold: float = 0.5

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
