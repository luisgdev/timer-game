"""Main module"""
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.core.database import init_db
from app.routers import auth, games

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager"""
    init_db()
    yield


app = FastAPI(
    title="Time it right Game",
    description="A timer-based game where users try to stop exactly at 10 seconds",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router=auth.router)
app.include_router(router=games.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Server is healthy."}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
