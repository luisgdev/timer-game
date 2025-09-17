"""Repository layer"""
import uuid
from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar

T = TypeVar("T")


class AbstractRepository(ABC, Generic[T]):
    """Abstract Repository Class"""

    @abstractmethod
    def create(self, item: T, db_session) -> T:
        """Create items"""
        raise NotImplementedError

    @abstractmethod
    def get_all(self, db_session) -> List[T]:
        """List items"""
        raise NotImplementedError

    @abstractmethod
    def get(self, item_id: int | uuid.UUID | str, db_session) -> T | None:
        """Get item by ID"""
        raise NotImplementedError

    @abstractmethod
    def update(self, updated_item: T, db_session) -> T:
        """Update item"""
        raise NotImplementedError

    @abstractmethod
    def delete(self, item: T, db_session) -> T:
        """Delete item"""
        raise NotImplementedError


class AbstractRepositoryUsers(AbstractRepository, Generic[T]):
    """Abstract Repository Class"""

    @abstractmethod
    def get_by_email(self, email: str, db_session) -> T | None:
        """Get item by email"""
        raise NotImplementedError

    @abstractmethod
    def get_by_username(self, username: str, db_session) -> T | None:
        """Get item by username"""
        raise NotImplementedError


class AbstractRepositoryHasUser(AbstractRepository, Generic[T]):
    """Abstract Repository Class"""

    @abstractmethod
    def get_by_user_id(self, user_id: int | uuid.UUID | str, db_session) -> T | None:
        """Get item by user_id"""
