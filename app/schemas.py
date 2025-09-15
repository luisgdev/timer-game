"""Schemas module"""

from pydantic import BaseModel


class UserSignUp(BaseModel):
    """User sign up form"""

    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    """User login form"""

    username: str
    password: str


class Token(BaseModel):
    """Token data properties"""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data properties"""

    email: str | None = None


class CustomResponse(BaseModel):
    """Message model"""

    message: str
