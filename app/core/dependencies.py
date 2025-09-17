"""Dependencies module"""
import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from app.core.database import get_session
from app.models import User
from app.routers.auth import verify_token
from app.routers.auth.service import get_user_by_email

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)
) -> User:
    """Get user by token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = await verify_token(token, credentials_exception, session)
    if token_data is None:
        raise credentials_exception

    user = await get_user_by_email(email=token_data.email, session=session)
    if user is None:
        raise credentials_exception

    return user
