"""Models module"""
import uuid

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import List
from enum import Enum


class GameStatus(str, Enum):
    STARTED = "started"
    COMPLETED = "completed"


class TableBase(SQLModel):
    """Base table model"""
    id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class User(TableBase, table=True):
    __tablename__ = "users"

    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    # Relationships
    game_sessions: List["GameSession"] = Relationship(back_populates="user")


class GameSession(TableBase, table=True):
    __tablename__ = "game_sessions"

    user_id: int = Field(foreign_key="users.id", index=True)
    start_time: datetime = Field(default_factory=datetime.utcnow)
    stop_time: datetime | None = None
    duration_ms: int | None = None  # Duration in milliseconds
    deviation_ms: int | None = None  # Absolute deviation from target
    status: GameStatus = Field(default=GameStatus.STARTED)
    # Relationships
    user: User | None = Relationship(back_populates="game_sessions")
