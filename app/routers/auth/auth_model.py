import logging
from datetime import UTC, datetime, timedelta
from typing import Annotated, Any

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.app_config import app_config
from app.data.database.database import SessionDep
from app.data.image_models import UserModel
from app.data.interfaces.auth_types import Token, TokenData

logging.getLogger("passlib").setLevel(logging.ERROR)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
TokenDep = Annotated[str, Depends(oauth2_scheme)]

app = FastAPI()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def get_user(session: AsyncSession, username: str) -> UserModel | None:
    return (
        await session.execute(
            select(UserModel).filter(UserModel.username.ilike(username)),
        )
    ).scalar_one_or_none()


async def authenticate_user(
    session: AsyncSession, username: str, password: str,
) -> UserModel | None:
    user = await get_user(session, username)
    if not user or not user.hashed_password:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_user_token(session: AsyncSession, username: str, password: str) -> Token:
    user = await authenticate_user(session, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer") #noqa: S106


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None,
) -> str:
    to_encode: dict[str, Any] = data.copy()
    expire = datetime.now(UTC) + expires_delta if expires_delta else datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, app_config.password_secret, algorithm=ALGORITHM)


async def get_current_user(session: SessionDep, token: TokenDep) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, app_config.password_secret, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError as e:
        raise credentials_exception from e
    assert token_data.username is not None
    user = await get_user(session, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


UserDep = Annotated[UserModel, Depends(get_current_user)]
