import enum

from pydantic import BaseModel


class Role(enum.Enum):
    ADMIN = 1
    USER = 2


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    role: Role


class UserWithPw(User):
    hashed_password: str
