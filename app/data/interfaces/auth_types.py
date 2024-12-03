from pydantic import BaseModel

from app.data.enums.user_role import Role


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
