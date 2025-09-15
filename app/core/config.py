"""Config module"""

import secrets

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings class to get values from .env file"""

    DATABASE_URL: str = "sqlite:///./timer_game.db"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5
    ALGORITHM: str = "HS256"
    GAME_SESSION_EXPIRE_MINUTES: int = 30
    TARGET_TIME_MS: int = 10_000
    # Below is internal config
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
