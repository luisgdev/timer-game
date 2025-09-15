"""Authentication Service module"""

import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select

from app.core.config import settings
from app.models import TokenBlacklist, User
from app.schemas import TokenData, UserSignUp

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token with JWT ID."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Add JWT ID for token tracking
    jti = str(uuid.uuid4())
    to_encode.update({"exp": expire, "jti": jti})
    encoded_jwt = jwt.encode(to_encode, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt, jti


async def verify_token(token: str, credentials_exception, session: Session = None):
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception

        # Check if token is blacklisted (if session is provided)
        if session:
            jti = payload.get("jti")
            if jti and await is_token_blacklisted(jti, session):
                raise credentials_exception

        token_data = TokenData(email=email)
        return token_data
    except JWTError as error:
        raise credentials_exception from error


async def authenticate_user(email: str, password: str, session: Session) -> Optional[User]:
    """Authenticate a user with email and password."""
    user = await get_user_by_email(email, session)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


async def get_user_by_email(email: str, session: Session) -> Optional[User]:
    """Get a user by email."""
    statement = select(User).where(User.email == email)
    result = session.exec(statement)
    user = result.first()
    return user


async def create_user(user_create: UserSignUp, session: Session) -> User:
    """Create a new user."""
    # Check if user already exists
    existing_user = await get_user_by_email(user_create.email, session)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Check if username already exists
    statement = select(User).where(User.username == user_create.username)
    result = session.exec(statement)
    if result.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
        )

    # Create new user
    user = User(
        email=user_create.email,
        username=user_create.username,
        is_active=True,
        password_hash=get_password_hash(user_create.password),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


async def add_token_to_blacklist(
    token_jti: str, user_id: uuid.UUID, expires_at: datetime, session: Session
) -> bool:
    """Add a token to the blacklist."""
    statement = select(TokenBlacklist).where(TokenBlacklist.token_jti == token_jti)
    result = session.exec(statement)
    token_blacklisted = result.first()
    if token_blacklisted:
        return False
    blacklisted_token = TokenBlacklist(token_jti=token_jti, user_id=user_id, expires_at=expires_at)
    session.add(blacklisted_token)
    session.commit()
    return True


async def is_token_blacklisted(token_jti: str, session: Session) -> bool:
    """Check if a token is blacklisted."""
    statement = select(TokenBlacklist).where(TokenBlacklist.token_jti == token_jti)
    result = session.exec(statement)
    blacklisted_token = result.first()
    return blacklisted_token is not None


async def logout_user(token: str, session: Session) -> bool:
    """Logout user by blacklisting their token."""
    try:
        # Decode token to get JWT ID and expiration
        payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        jti = payload.get("jti")
        exp = payload.get("exp")

        if not jti or not exp:
            return False

        # Convert exp timestamp to datetime
        expires_at = datetime.fromtimestamp(exp)

        # Get user ID from token
        email = payload.get("sub")
        if not email:
            return False

        user = await get_user_by_email(email, session)
        if not user:
            return False

        # Add token to blacklist
        result = await add_token_to_blacklist(jti, user.id, expires_at, session)
        return result

    except JWTError:
        return False
