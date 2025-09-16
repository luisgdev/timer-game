"""Analytics module"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, func, select

from app.core.database import get_session
from app.core.dependencies import get_current_user
from app.models import GameSession, GameStatus, User
from app.routers.games.service import calculate_accuracy_percentage
from app.schemas import GameSessionResponse, UserStats

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/user/{user_id}", response_model=UserStats)
async def get_user_stats(
    user_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Get user
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Get all game sessions
    all_sessions = session.exec(
        select(GameSession)
        .where(GameSession.user_id == user_id)
        .order_by(GameSession.created_at.desc())
    ).all()

    # Get completed sessions for statistics
    completed_sessions = [s for s in all_sessions if s.status == GameStatus.COMPLETED]

    # Calculate statistics
    total_games = len(all_sessions)
    completed_games = len(completed_sessions)

    if completed_games > 0:
        deviations = [s.deviation_ms for s in completed_sessions]
        avg_deviation = sum(deviations) / len(deviations)
        best_deviation = min(deviations)
        worst_deviation = max(deviations)
        avg_accuracy = calculate_accuracy_percentage(int(avg_deviation))
    else:
        avg_deviation = None
        best_deviation = None
        worst_deviation = None
        avg_accuracy = None

    # Get recent games (last 10)
    recent_games = [
        GameSessionResponse(
            id=s.id,
            start_time=s.start_time,
            stop_time=s.stop_time,
            duration_ms=s.duration_ms,
            deviation_ms=s.deviation_ms,
            status=s.status,
        )
        for s in all_sessions[:10]
    ]

    return UserStats(
        user_id=user.id,
        username=user.username,
        total_games=total_games,
        completed_games=completed_games,
        average_deviation_ms=round(avg_deviation, 2) if avg_deviation else None,
        best_deviation_ms=best_deviation,
        worst_deviation_ms=worst_deviation,
        average_accuracy=avg_accuracy,
        recent_games=recent_games,
    )
