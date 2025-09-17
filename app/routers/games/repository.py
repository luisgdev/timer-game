"""Repository Layer"""
import uuid
from typing import List

from sqlmodel import select

from app.core.repository import AbstractRepositoryHasUser
from app.models import GameSession, GameStatus


class GameRepository(AbstractRepositoryHasUser):
    """Game Session Repository"""

    def get_by_user_id(self, user_id: uuid.UUID, db_session) -> GameSession | None:
        """Get ACTIVE game session by user_id"""
        active_session = db_session.exec(
            select(GameSession).where(
                GameSession.user_id == user_id, GameSession.status == GameStatus.STARTED
            )
        ).first()
        return active_session

    def get(self, item_id: uuid.UUID, db_session) -> GameSession | None:
        """Get an ACTIVE game session by ID"""
        active_session = db_session.exec(
            select(GameSession).where(
                GameSession.id == item_id, GameSession.status == GameStatus.STARTED
            )
        ).first()
        return active_session

    def create(self, item: GameSession, db_session) -> GameSession:
        """Create a game session"""
        db_session.add(item)
        db_session.commit()
        db_session.refresh(item)
        return item

    def get_all(self, db_session) -> List[GameSession]:
        pass

    def update(self, updated_item: GameSession, db_session) -> GameSession:
        """UPDATE an ACTIVE game session"""
        db_session.add(updated_item)
        db_session.commit()
        db_session.refresh(updated_item)
        return updated_item

    def delete(self, item: GameSession, db_session) -> GameSession:
        pass
