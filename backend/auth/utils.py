from passlib.context import CryptContext
import jwt
from sqlalchemy.exc import IntegrityError
from auth.schemas import PermissionEnum
from models import Usr, Token
from datetime import datetime
from typing import Annotated
from fastapi import Depends, Request, status, HTTPException
from database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from config import settings
from dao import (
	PermissionManager,
	UsrManager,
	TokenManager,
	UsrGroupManager,
)
from typing import List
import logging


logger = logging.getLogger(__name__)

ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=['bcrypt'])


async def verify_token(
	access_token,
	session: Annotated[AsyncSession, Depends(get_async_session)],
):
	try:
		db_token = await TokenManager.get_one_by(session, token=access_token)
	except Exception:
		raise HTTPException(status_code=404, detail='Token not found')
	return db_token.token


async def get_token(
	request: Request,
	session: Annotated[AsyncSession, Depends(get_async_session)],
) -> Token:
	"""get token from cookies or headers"""
	access_token = request.cookies.get('access_token')

	if not access_token:
		access_token = request.headers.get('Authorization')

	if access_token:
		return await verify_token(access_token, session)

	else:
		raise HTTPException(
			status_code=401,
			detail='Token not found in header or cookies',
		)


def get_hashed_password(password):
	return pwd_context.hash(password)


def verify_password(password, hashed_password):
	return pwd_context.verify(password, hashed_password)


async def authenticate_user(
	email: str,
	password: str,
	session: Annotated[AsyncSession, Depends(get_async_session)],
) -> Usr:
	# получение позльзователя
	user: Usr = await UsrManager.get_one_by(session, email=email)

	if not verify_password(password, user.hashed_password):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail='Incorrect email or password',
		)
	return user


async def create_access_token(session: AsyncSession, user: Usr, data: dict):
	to_encode = data.copy()
	to_encode.update({'created': datetime.utcnow().strftime('%d%H%M%S')})
	encoded_jwt = jwt.encode(
		to_encode,
		settings.JWT_SECRET_KEY,
		algorithm=settings.JWT_ALGORITHM,
	)
	token = Token(token=encoded_jwt, user=user, user_id=user.id)
	await TokenManager.create(session, token)
	try:
		await session.flush()
		return token.token

	except IntegrityError as e:
		print(e)
		return None


async def get_current_user(
	session: Annotated[AsyncSession, Depends(get_async_session)],
	token: Annotated[str, Depends(get_token)],
):
	# получение пользователя по токену
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail='Could not validate credentials',
		headers={'WWW-Authenticate': 'Bearer'},
	)
	user = await TokenManager.get_user_by_token(session, token=token)

	if user is None:
		raise credentials_exception
	return user


async def get_current_active_user(
	current_user: Annotated[Usr, Depends(get_current_user)],
) -> Usr:
	if not current_user.is_active:
		raise HTTPException(status_code=400, detail='Inactive user')
	return current_user


async def list_permissions(
	session: Annotated[AsyncSession, Depends(get_async_session)],
	user_id: int,
	group_id,
):
	return await UsrGroupManager.get_permissions(session, user_id, group_id)


async def my_list_permissions(
	session: Annotated[AsyncSession, Depends(get_async_session)],
	user: Annotated[Usr, Depends(get_current_active_user)],
	group_id,
):
	return await list_permissions(session, user.id, group_id)


async def my_priority_role(
	session: Annotated[AsyncSession, Depends(get_async_session)],
	user: Annotated[Usr, Depends(get_current_active_user)],
	group_id: int,
):
	return await UsrGroupManager.get_priority_role(session, user.id, group_id=group_id)


async def get_list_permissions_in(
	session: Annotated[AsyncSession, Depends(get_async_session)],
	permissions: List[PermissionEnum],
):
	return await PermissionManager.get_permissions_in(session, permissions)
