from os import access
from passlib.context import CryptContext
import jwt
from .dao import UserManager, TokenManager
from .models import User, Token
from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import Depends, Request, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from database import async_session_maker

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"])

async def verify_token(access_token):
    async with async_session_maker() as session:
        try:
            db_token = await TokenManager.get_one_by(session, token=access_token)
        except:
            raise HTTPException(status_code=404, detail="Token not found")
    return db_token

async def get_token_cookie(request: Request) -> Token:
    access_token = request.cookies.get("access_token")
    
    if access_token:
        return await verify_token(access_token)
    else:
        raise HTTPException(status_code=401, detail="Token not found in header or cookies")



def get_hashed_password(password):
    return pwd_context.hash(password)

def verify_password(password, hashed_password):
    return pwd_context.verify(password, hashed_password)

async def authenticate_user(username: str, password: str) -> User | None:
    #получение позльзователя
    async with async_session_maker() as session:
        user: User | None = await UserManager.get_one_by(session, email=username)

    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

async def create_access_token(user: User, data: dict, expires_delta: timedelta | None = None):
    #создание токена
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    token = Token(token=encoded_jwt, user=user)

    async with async_session_maker() as session:
        await TokenManager.add(session, token)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(get_token_cookie)]):
    #получение пользователя по токену
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    async with async_session_maker() as session:
        user = await TokenManager.get_user_by_token(session, token=token.token)
    
    if user is None:
        raise credentials_exception
    return user    

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


