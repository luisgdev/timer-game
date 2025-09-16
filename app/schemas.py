"""Schemas module"""
import uuid
from datetime import datetime
from typing import List

from pydantic import BaseModel

from app.models import GameStatus


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


class LeaderboardEntry(BaseModel):
    """Leaderboard entry model"""

    rank: int
    username: str
    total_games: int
    average_deviation_ms: float
    best_deviation_ms: int
    accuracy_percentage: float


class LeaderboardResponse(BaseModel):
    """Leaderboard response model"""

    entries: List[LeaderboardEntry]
    page: int
    total_pages: int
    total_players: int


class GameSessionResponse(BaseModel):
    """Game session details"""

    id: uuid.UUID
    start_time: datetime
    stop_time: datetime | None
    duration_ms: int | None
    deviation_ms: int | None
    status: GameStatus


# Analytics Schemas
class UserStats(BaseModel):
    """User stats"""

    user_id: uuid.UUID
    username: str
    total_games: int
    completed_games: int
    average_deviation_ms: float | None
    best_deviation_ms: int | None
    worst_deviation_ms: int | None
    average_accuracy: float | None
    recent_games: List[GameSessionResponse]
