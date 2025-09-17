"""Repository layer"""
from typing import List

from sqlmodel import Session, select

from app.core.repository import AbstractRepository, AbstractRepositoryUsers
from app.models import TokenBlacklist, User


class UserRepository(AbstractRepositoryUsers[User]):
    """User repository"""

    def get_by_email(self, email: str, db_session: Session) -> User | None:
        """Get user by email"""
        statement = select(User).where(User.email == email)
        result = db_session.exec(statement)
        return result.first()

    def get_by_username(self, username: str, db_session: Session) -> User | None:
        """Get user by username"""
        statement = select(User).where(User.username == username)
        result = db_session.exec(statement)
        return result.first()

    def get(self, item_id, db_session: Session) -> User | None:
        """Get User by ID"""
        statement = select(User).where(User.id == item_id)
        result = db_session.exec(statement)
        return result.first()

    def create(self, item: User, db_session: Session) -> User:
        """Create new user"""
        db_session.add(item)
        db_session.commit()
        db_session.refresh(item)
        return item

    def get_all(self, db_session: Session) -> List[User]:
        """List all users"""

    def update(self, updated_item: User, db_session: Session) -> User:
        """Update user"""

    def delete(self, item: User, db_session: Session) -> User:
        """Delete user"""


class TokenBlacklistRepository(AbstractRepository[TokenBlacklist]):
    """Token blacklist repository"""

    def create(self, item: TokenBlacklist, db_session: Session) -> TokenBlacklist:
        """Record token blacklist"""
        db_session.add(item)
        db_session.commit()
        db_session.refresh(item)
        return item

    def get(self, item_id, db_session: Session) -> TokenBlacklist | None:
        """Get blacklisted token by ID"""
        statement = select(TokenBlacklist).where(TokenBlacklist.token_jti == item_id)
        result = db_session.exec(statement)
        return result.first()

    def get_all(self, db_session: Session) -> List[TokenBlacklist]:
        """List blacklisted tokens"""

    def update(self, updated_item: TokenBlacklist, db_session: Session) -> TokenBlacklist:
        """Update blacklisted token"""

    def delete(self, item: TokenBlacklist, db_session: Session) -> TokenBlacklist:
        """Delete blacklisted token"""
