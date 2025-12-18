from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Supabase
    supabase_url: str
    supabase_key: str  # anon key
    supabase_service_key: str = ""  # service role key (可选)
    supabase_jwt_secret: str
    supabase_db_url: str

    # DeepSeek API
    deepseek_api_key: str
    deepseek_base_url: str = "https://api.deepseek.com/v1"

    # App
    app_name: str = "HistoriaQuest API"
    debug: bool = False
    cors_origins: list[str] = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
