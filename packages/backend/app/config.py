from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='VDL_', env_file='.env', extra='ignore')

    db_url: str = 'sqlite:///./vendandlog.db'
    frontend_build_dir: Path = Path(__file__).resolve().parents[2] / 'frontend' / 'build'
    serve_frontend: bool = True
    cors_origins: list[str] = []


@lru_cache
def get_settings() -> Settings:
    return Settings()
