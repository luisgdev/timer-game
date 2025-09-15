"""Games module"""
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.database import get_session
from app.core.dependencies import get_current_user
from app.models import GameSession, GameStatus, User
from app.routers.games.service import (
    calculate_accuracy_percentage,
    calculate_deviation_ms,
    calculate_duration_ms,
    create_game_session,
    get_performance_message,
    get_session_by_id,
    get_session_by_user,
    is_session_expired,
    update_game_session_status,
)
from app.schemas import CustomResponse, GameStartResponse, GameStopResponse

router = APIRouter(prefix="/games", tags=["Games"])


@router.post("/start", response_model=GameStartResponse)
async def start_game(
    current_user: User = Depends(get_current_user), db_session: Session = Depends(get_session)
):
    """Start a new game."""
    active_session = await get_session_by_user(db_session, current_user)
    if active_session:
        # Check if it's expired
        if is_session_expired(active_session.start_time):
            active_session.status = GameStatus.EXPIRED
            update_game_session_status(
                game_session=active_session, status=GameStatus.EXPIRED, db_session=db_session
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"You already have an active game session (ID: {active_session.id})",
            )

    game_session = create_game_session(
        game_session=GameSession(
            user_id=current_user.id, start_time=datetime.utcnow(), status=GameStatus.STARTED
        ),
        db_session=db_session,
    )

    return GameStartResponse(session_id=game_session.id, start_time=game_session.start_time)


@router.post("/{session_id}/stop", response_model=GameStopResponse)
async def stop_game(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_session),
):
    """Stop a game."""
    game_session = await get_session_by_id(db_session=db_session, game_id=session_id)

    if not game_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game session not found")

    # Verify ownership
    if game_session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only stop your own game sessions",
        )

    # Check if already completed
    if game_session.status == GameStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This game session has already been completed",
        )

    # Check if expired
    if is_session_expired(game_session.start_time):
        game_session.status = GameStatus.EXPIRED
        db_session.add(game_session)
        db_session.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="This game session has expired"
        )

    # Calculate results
    stop_time = datetime.utcnow()
    duration_ms = calculate_duration_ms(game_session.start_time, stop_time)
    deviation_ms = calculate_deviation_ms(duration_ms)
    accuracy = calculate_accuracy_percentage(deviation_ms)

    # Update game session
    game_session.stop_time = stop_time
    game_session.duration_ms = duration_ms
    game_session.deviation_ms = deviation_ms
    game_session.status = GameStatus.COMPLETED

    db_session.add(game_session)
    db_session.commit()

    return GameStopResponse(
        session_id=game_session.id,
        duration_ms=duration_ms,
        deviation_ms=deviation_ms,
        accuracy_percentage=accuracy,
        message=get_performance_message(deviation_ms),
    )
