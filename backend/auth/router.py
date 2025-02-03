import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, Form, status, Response
from datetime import timedelta
from models import Usr
from .utils import (
	authenticate_user,
	create_access_token,
	get_current_active_user,
	get_hashed_password,
	get_token,
	list_permissions,
	my_list_permissions,
)
from dao import UsrManager, TokenManager, UsrGroupManager
from .schemas import UsrRead
from database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from auth.smtp import send_message
from config import settings
from models import Token
from random import randint

ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(prefix='/api/auth', tags=['auth'])


@router.post('/register')
async def register(
	name: Annotated[str, Form()],
	email: Annotated[str, Form()],
	password: Annotated[str, Form()],
	session: Annotated[AsyncSession, Depends(get_async_session)],
):
	try:
		hashed_password = get_hashed_password(password)
		random_num_for_name_account = randint(1000, 9999)
		user_db = Usr(
			name=name,
			name_account=name + '#' + str(random_num_for_name_account),
			email=email,
			hashed_password=hashed_password,
			is_active=True,
			is_verified=False,
			is_superuser=False,
		)
		await UsrManager.create(session, user_db)
		token = await create_access_token(
			session=session, user=user_db, data={'email': user_db.email}
		)
		await session.commit()
		await send_message(
			email,
			'Verification code',
			f'Перейдите по ссылке: {settings.BASE_URL}/api/auth/verify/{token}',
		)  # отправка письма с токеномtoken)
		return {'status': status.HTTP_200_OK}
	except Exception:
		return {'status': status.HTTP_400_BAD_REQUEST, 'exception': Exception}


@router.post('/login')
@router.post('/create_token')
async def login_for_access_token(
	response: Response,
	session: Annotated[AsyncSession, Depends(get_async_session)],
	email: str = Form(),
	password: str = Form(),
):
	"""
	/login и /token - это один и тот же эндпоинт
	"""
	# создание токена при созданном пользователе

	user: Usr = await authenticate_user(email, password, session)

	access_token = await create_access_token(
		session=session, user=user, data={'email': user.email}
	)
	await session.commit()
	expires = datetime.datetime.utcnow() + datetime.timedelta(days=30)
	expires_str = expires.astimezone(datetime.timezone.utc)

	response.set_cookie(
		key='access_token',
		value=access_token,
		httponly=True,
		samesite='none',
		secure=True,
	)
	return {'access_token': access_token}


@router.get('/get_token')
async def get_token(token: Annotated[Token, Depends(get_token)]):
	return token


@router.get('/users/me')
async def users_me(
	current_user: Annotated[Usr, Depends(get_current_active_user)],
) -> UsrRead:
	return current_user


@router.get('/verify/{token}')
async def verify(
	token: str, session: Annotated[AsyncSession, Depends(get_async_session)]
):
	token = await TokenManager.get_one_by(session, token=token)
	user = await UsrManager.get_one_by(session, id=token.user_id)
	await TokenManager.delete(session, token)
	user.is_verified = True
	await session.commit()
	return {'status': status.HTTP_200_OK}


@router.get('/permissions')
async def permissions(
	param_permissions: Annotated[str, Depends(list_permissions)],
):
	return param_permissions


@router.get('/permissions/me')
async def permissions_me(
	param_permissions: Annotated[str, Depends(my_list_permissions)],
):
	return param_permissions
