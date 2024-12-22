from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.data.database.database import SessionDep
from app.data.image_models import UserModel
from app.data.interfaces.auth_types import Token, User
from app.routers.auth.auth_model import UserDep, get_user_token

auth_router = APIRouter(tags=["auth"])


@auth_router.post("/token")
async def login_for_access_token(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    return await get_user_token(session, form_data.username, form_data.password)


@auth_router.get("/users/me/", response_model=User)
async def read_users_me(current_user: UserDep) -> UserModel:
    return current_user
