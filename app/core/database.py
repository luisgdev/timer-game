"""Database module"""

from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=False,
)


def init_db():
    """Initialize the database"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Return a SQLModel session"""
    with Session(engine) as session:
        yield session
