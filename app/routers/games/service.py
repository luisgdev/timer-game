"""Games service module"""
import uuid
from datetime import datetime, timedelta

from sqlmodel import Session

from app.core.config import settings
from app.models import GameSession, GameStatus, User
from app.routers.games.repository import GameRepository

game_db = GameRepository()


async def get_session_by_user(db_session: Session, user: User) -> GameSession | None:
    """Check if a game session exists for a user."""
    active_session = game_db.get_by_user_id(user_id=user.id, db_session=db_session)
    return active_session


async def get_session_by_id(db_session: Session, game_id: uuid.UUID) -> GameSession | None:
    """Check if a game session exists by ID."""
    active_session = game_db.get(item_id=game_id, db_session=db_session)
    return active_session


def update_game_session_status(
    db_session: Session, game_session: GameSession, status: GameStatus
) -> GameSession:
    """Update a game session status."""
    game_session.status = status
    result = game_db.update(updated_item=game_session, db_session=db_session)
    return result


def create_game_session(db_session: Session, game_session: GameSession) -> GameSession:
    """Save a game session."""
    result = game_db.create(item=game_session, db_session=db_session)
    return result


def calculate_duration_ms(start_time: datetime, stop_time: datetime) -> int:
    """Calculate duration in milliseconds"""
    duration = stop_time - start_time
    return int(duration.total_seconds() * 1000)


def calculate_deviation_ms(duration_ms: int) -> int:
    """Calculate absolute deviation from target time"""
    return abs(duration_ms - settings.TARGET_TIME_MS)


def calculate_accuracy_percentage(deviation_ms: int) -> float:
    """Calculate accuracy as a percentage (100% = perfect)"""
    if deviation_ms == 0:
        return 100.0
    # Max deviation considered is the target time itself
    max_deviation = settings.TARGET_TIME_MS
    accuracy = max(0, (1 - (deviation_ms / max_deviation))) * 100
    return round(accuracy, 2)


def is_session_expired(start_time: datetime) -> bool:
    """Check if a game session has expired"""
    expiry_time = start_time + timedelta(minutes=settings.GAME_SESSION_EXPIRE_MINUTES)
    return datetime.utcnow() > expiry_time


def get_performance_message(deviation_ms: int) -> str:
    """Generate a performance message based on deviation"""
    if deviation_ms == 0:
        text = "PERFECT! Exactly 10 seconds! 🎯"
    elif deviation_ms < 50:
        text = "Incredible! Almost perfect timing! 🌟"
    elif deviation_ms < 100:
        text = "Excellent timing! Very close! ⭐"
    elif deviation_ms < 250:
        text = "Great job! Pretty accurate! 👍"
    elif deviation_ms < 500:
        text = "Good attempt! Keep practicing! 💪"
    elif deviation_ms < 1000:
        text = "Not bad! Room for improvement. 📈"
    else:
        text = "Keep trying! Practice makes perfect. 🎮"
    return text
