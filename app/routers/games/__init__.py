"""Games module"""

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.models import User
from app.schemas import CustomResponse

router = APIRouter(prefix="/games", tags=["Games"])


@router.post("/start", response_model=CustomResponse)
async def start_game(current_user: User = Depends(get_current_user)):
    """Start a new game."""
    return {"message": f"Games has started, {current_user.username}"}


@router.post("/stop", response_model=CustomResponse)
async def stop_game(current_user: User = Depends(get_current_user)):
    """Stop a game."""
    return {"message": f"Games has stopped, {current_user.username}"}
