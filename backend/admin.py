from auth.utils import authenticate_user
from fastapi.requests import Request
from db.models import Chat, Group, Message, Token, Usr
from sqladmin import ModelView
from sqladmin.authentication import AuthenticationBackend


class UsrAdmin(ModelView, model=Usr):
    column_list = [
        'id',
        'name',
        'email',
        'is_active',
        'is_verified',
        'is_superuser',
        'tokens',
    ]

    column_formatters = {'token': lambda m, a: [i.id for i in m.tokens]}


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
        email: str = form['email']
        password: str = form['password']

        user = await authenticate_user(email, password)
        if not user:
            return False

        if user.is_superuser:
            request.session.update({'token': '...'})
            return True

        return False

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get('token')

        if not token:
            return False

        # Check the token in depth
        return True


def add_views(admin):
    model_admin = [UsrAdmin, GroupAdmin, MessageAdmin, TokenAdmin, ChatAdmin]
    [admin.add_view(item) for item in model_admin]
