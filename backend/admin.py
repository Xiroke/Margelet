from audioop import add
from sqladmin import ModelView
from sqladmin.authentication import AuthenticationBackend
from fastapi.requests import Request
from auth.models import User, Token, Group, Message, Chat
from auth.utils import get_hashed_password, authenticate_user
from config import settings
from database import get_async_session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select


async def admin_seed():
    async for session in get_async_session():
        if (await session.execute(select(User))).first():
            return

        try:
            hashed_passwrod = get_hashed_password(settings.ADMIN_PASSWORD)
            admin = User(name=settings.ADMIN_NAME, email=settings.ADMIN_EMAIL, hashed_password=hashed_passwrod, is_active=True, is_verified=True, is_superuser=True)
            session.add(admin)
            await session.commit()
        except IntegrityError as e:
            #конфликт с несколькими воркерами при использовании этой функции в on_startup
            pass

class UserAdmin(ModelView, model=User):
    column_list = ['id', 'name', 'email', 'is_active', 'is_verified', 'is_superuser', 'tokens']

    column_formatters = {
        'token': lambda m, a: [i.id for i in m.tokens]
    }

class GroupAdmin(ModelView, model=Group):
    column_list = ['id', 'title', 'description', 'users', 'chats']

class MessageAdmin(ModelView, model=Message):
    column_list = ['id', 'local_id', 'message', 'user', 'chat']

class TokenAdmin(ModelView, model=Token):
    column_list = ['id', 'title', 'token', 'user']

class ChatAdmin(ModelView, model=Chat):
    column_list = ['id', 'title', 'messages', 'description', 'group']

class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username: str = form["username"]
        password: str = form["password"]

        user = await authenticate_user(username, password)
        if not user:
            return False

        if user.is_superuser: 
            request.session.update({"token": "..."})
            return True

        return False


    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        # Check the token in depth
        return True


def add_views(admin):
    model_admin = [UserAdmin, GroupAdmin, MessageAdmin, TokenAdmin, ChatAdmin]
    [admin.add_view(item) for item in model_admin]