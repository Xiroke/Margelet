from typing import Annotated, Dict, List
from fastapi import (
    Depends,
    FastAPI,
    Header,
    Query,
    Request,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session
from config import settings
from auth.utils import (
    get_current_active_user,
    get_hashed_password,
    create_access_token,
    verify_token,
)
from bots.utils import get_no_read_messages
from models import Usr
from auth.schemas import BotUsrCreate
from dao import UsrManager, TokenManager
from chat.router import connection_manager_users
from .shemas import BotWebsocketReceived
from messages.shemas import MessageRead

app = FastAPI(
    debug=settings.DEBUG,
    openapi_url='/openapi.json',
    docs_url='/docs',
    redoc_url='/redoc',
)

origins = [
    'http://localhost.tiangolo.com',
    'https://localhost.tiangolo.com',
    'http://localhost',
    'http://localhost:8080',
    'http://localhost:60',
    'http://localhost:3000',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://127.0.0.1:8080',
    'http://127.0.0.1:3000',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/')
async def ping():
    """Test works"""
    return 'ping'


@app.get('/no_read_messages')
async def no_read_messages(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[Usr, Depends(get_current_active_user)],
) -> List[MessageRead]:
    """Get all messassges that not read"""
    return await get_no_read_messages(session, user)


@app.post('/create_bot')
async def create_bot(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user_create: Annotated[BotUsrCreate, Depends()],
):
    """Create bot"""
    hashed_password = get_hashed_password(user_create.password)
    bot_user = Usr(
        name=user_create.name,
        name_account=user_create.name_account,
        email=user_create.name_account + '@marglelet.bot',
        hashed_password=hashed_password,
        is_bot=True,
    )
    await UsrManager.create(session, bot_user)
    await session.commit()
    token = await create_access_token(session, bot_user)
    return token


# @app.post('/send_message/{to_chat_id}')
# async def send_message(
# 	session: Annotated[AsyncSession, Depends(get_async_session)],
# 	user: Annotated[Usr, Depends(get_current_active_user)],
# 	to_chat_id: int,
# ):
# 	return 'good'


class ConnectionManagerBot:
    def __init__(self):
        self.active_connections_bot: Dict[int, WebSocket] = {} # id: ws

    async def connect_bot(self, websocket: WebSocket, bot_id: int):
        await websocket.accept()

        if bot_id not in self.active_connections_bot.keys():
            self.active_connections_bot[bot_id] = []
        self.active_connections_bot[bot_id].append(websocket)

    def disconnect_bot(self, websocket, bot_id: int):
        self.active_connections_bot[bot_id].remove(websocket)


bot_manager = ConnectionManagerBot()


@app.websocket('/bot')
async def bot_websocket(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    websocket: WebSocket,
    token: Annotated[str | None, Query()] = None,
):
    """Websocket for sending messages to users"""
    await verify_token(token, session)
    bot = await TokenManager.get_user_by_token(session, token)
    await bot_manager.connect_bot(websocket, bot.id)
    try:
        while True:
            data_json = await websocket.receive_json()
            data = BotWebsocketReceived(**data_json)
            await connection_manager_users.broadcast(text=data.text, chat_id=data.chat_id, access_token=token, session=session)

    except WebSocketDisconnect:
        bot_manager.disconnect_bot(websocket, bot.id)
