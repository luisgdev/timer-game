"""Schemas module"""
import uuid
from datetime import datetime

from pydantic import BaseModel


class UserSignUp(BaseModel):
    """User sign up form"""

    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    """User login form"""

    username: str
    password: str


class Token(BaseModel):
    """Token data properties"""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data properties"""

    email: str | None = None


class CustomResponse(BaseModel):
    """Message model"""

    message: str


class GameStartResponse(BaseModel):
    """Response when game starts"""

    session_id: int | str | uuid.UUID
    start_time: datetime
    message: str = "Timer started! Try to stop at exactly 10 seconds."


class GameStopResponse(BaseModel):
    """Response when game is stopped"""

    session_id: int | str | uuid.UUID
    duration_ms: int
    deviation_ms: int
    accuracy_percentage: float
    message: str
