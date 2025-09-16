"""Leaderboard router module"""
import math

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, func, select

from app.core.database import get_session
from app.core.dependencies import get_current_user
from app.models import GameSession, GameStatus, User
from app.routers.games.service import calculate_accuracy_percentage
from app.schemas import LeaderboardEntry, LeaderboardResponse

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])


@router.get("", response_model=LeaderboardResponse)
async def get_leaderboard(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Subquery for user statistics
    subquery = (
        select(
            GameSession.user_id,
            func.count(GameSession.id).label("total_games"),
            func.avg(GameSession.deviation_ms).label("avg_deviation"),
            func.min(GameSession.deviation_ms).label("best_deviation"),
        )
        .where(GameSession.status == GameStatus.COMPLETED)
        .group_by(GameSession.user_id)
        .subquery()
    )

    # Main query joining users with their stats
    query = (
        select(
            User.username,
            subquery.c.total_games,
            subquery.c.avg_deviation,
            subquery.c.best_deviation,
        )
        .join(subquery, User.id == subquery.c.user_id)
        .order_by(subquery.c.avg_deviation)
    )

    # Get total count
    total_query = select(func.count()).select_from(subquery)
    total_players = session.exec(total_query).first()

    # Calculate pagination
    total_pages = math.ceil(total_players / per_page) if total_players else 0
    offset = (page - 1) * per_page

    # Execute paginated query
    results = session.exec(query.offset(offset).limit(per_page)).all()

    # Build leaderboard entries
    entries = []
    for idx, (username, total_games, avg_deviation, best_deviation) in enumerate(
        results, start=offset + 1
    ):
        accuracy = calculate_accuracy_percentage(int(avg_deviation))
        entries.append(
            LeaderboardEntry(
                rank=idx,
                username=str(username),
                total_games=total_games,
                average_deviation_ms=round(avg_deviation, 2),
                best_deviation_ms=best_deviation,
                accuracy_percentage=accuracy,
            )
        )

    return LeaderboardResponse(
        entries=entries, page=page, total_pages=total_pages, total_players=total_players or 0
    )
