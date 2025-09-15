"""Config module"""

import secrets

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings class to get values from .env file"""

    DATABASE_URL: str = "sqlite:///./timer_game.db"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5
    ALGORITHM: str = "HS256"
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
