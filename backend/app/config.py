from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str
    model_name: str = "claude-haiku-4-5"
    rate_limit: str = "5/hour"

@lru_cache
def get_settings() -> Settings:
    return Settings()
