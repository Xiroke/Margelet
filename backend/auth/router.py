from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from .models import User
from .utils import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_hashed_password,
    get_token_cookie
)
from .dao import UserManager
from .schemas import UserCreate, JWTTokenSchema, UserRead
from database import async_session_maker
from config import settings


ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register")
async def register(user: Annotated[UserCreate, Depends()]):
    try:
        hashed_password = get_hashed_password(user.password)
        user_db = User(
            name=user.name,
            email=user.email,
            hashed_password=hashed_password,
            is_active=True,
            is_verified=True,
            is_superuser=False,
        )
        async with async_session_maker() as session:
            await UserManager.add(session, user_db)

        return {"status": status.HTTP_201_CREATED}
    except Exception:
        return {"status": status.HTTP_400_BAD_REQUEST, "exception": Exception}


@router.post("/login")
@router.post("/create_token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], response: Response
):
    '''
    /login и /token - это один и тот же эндпоинт

    Примечание:
        username - это email

    Возвращает токен
    '''
    # создание токена при созданном пользователе
    user: User | None = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        user=user, data={"email": user.email}, expires_delta=access_token_expires
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="none",
        secure=True
    )
    return access_token

@router.get("/get_token")
async def get_token(token: Annotated[str, Depends(get_token_cookie)]):
    return token

@router.get("/users/me/")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserRead:
    return UserRead.model_validate(current_user)
