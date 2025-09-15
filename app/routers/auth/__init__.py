"""Authentication module"""

import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session

from app.core.config import settings
from app.core.database import get_session
from app.models import User
from app.routers.auth.service import (
    authenticate_user,
    create_access_token,
    create_user,
    get_user_by_email,
    logout_user,
    verify_token,
)
from app.schemas import CustomResponse, Token, UserSignUp

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)
) -> User:
    """Get the current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = await verify_token(token, credentials_exception, session)
    user = await get_user_by_email(token_data.email, session)
    if user is None:
        raise credentials_exception
    return user


@router.post("/register", response_model=User)
async def register(user_create: UserSignUp, session: Session = Depends(get_session)):
    """Register a new user account."""
    try:
        user = await create_user(user_create, session)
        return user
    except (HTTPException, Exception) as error:
        logger.error(error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration",
        ) from error


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)
):
    """Authenticate user and return JWT token."""
    user = await authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token, _ = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout", response_model=CustomResponse)
async def logout(
    session: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme),
):
    """Logout user by blacklisting their current token."""
    success = await logout_user(token, session)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to logout. Invalid token."
        )

    return CustomResponse(message="Successfully logged out")
