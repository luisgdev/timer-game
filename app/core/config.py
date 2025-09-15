"""Config module"""

from pydantic_settings import BaseSettings, SettingsConfigDict
import secrets

class Settings(BaseSettings):
    """Settings class to get values from .env file"""

    DATABASE_URL: str = "sqlite:///./timer_game.db"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
