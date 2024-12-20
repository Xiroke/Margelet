from os import access
from turtle import title
from fastapi import APIRouter, WebSocket, Query, Depends, status
from fastapi.responses import HTMLResponse
from fastapi.websockets import WebSocketDisconnect
from typing import Annotated, Dict, get_origin, List
from auth.dao import GroupManager, TokenManager, UserManager, ChatManager, MessageMenager
from auth.schemas import ListGroupRead, GroupRead
from database import async_session_maker
from sqlalchemy.ext.asyncio import AsyncSession
from auth.utils import get_current_active_user, verify_password, get_token_cookie, verify_token
from fastapi.security import OAuth2PasswordBearer
from auth.models import Chat, Token, User, Group, Message
from .schemas import Full_info_chat, Server_to_websocket_data, Websocket_to_server_data

router = APIRouter(prefix="/api/chat", tags=["chat"])

# html = """
# <!DOCTYPE html>
# <html>
#     <head>
#         <title>Chat</title>
#     </head>
#     <body>
#         <h1>WebSocket Chat</h1>
#         <form action="" onsubmit="sendMessage(event)">
#             <label>Item ID: <input type="text" id="itemId" autocomplete="off" value="foo"/></label>
#             <button onclick="connect(event)">Connect</button>
#             <hr>
#             <label>Message: <input type="text" id="messageText" autocomplete="off"/></label>
#             <button>Send</button>
#         </form>
#         <ul id='messages'>
#         </ul>
#         <script>
#         var ws = null;
#         var token = null;
        
#         // Get token first
#         fetch("/api/auth/get_token", {
#             method: "GET",
#             credentials: 'include'
#         })
#         .then(response => response.json())
#         .then(data => {
#             token = data;
#             console.log('Token received:', token);
#         })
#         .catch(error => console.error('Error fetching token:', error));

#         function connect(event) {
#             var itemId = document.getElementById("itemId")
#             ws = new WebSocket(`${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/chat?token=${token.access_token}`);
#             ws.onmessage = function(event) {
#                 var messages = document.getElementById('messages')
#                 var message = document.createElement('li')
#                 var content = document.createTextNode(event.data)
#                 message.appendChild(content)
#                 messages.appendChild(message)
#             };
#             event.preventDefault()
#         }
#             function sendMessage(event) {
#                 var input = document.getElementById("messageText")
#                 ws.send(input.value)
#                 input.value = ''
#                 event.preventDefault()
#             }
#         </script>
#     </body>
# </html>
# """

    
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Dict[int, List[WebSocket]]] = {}

    async def connect(self, websocket: WebSocket, group_id: int, chat_id: int):
        await websocket.accept()

        if group_id not in self.active_connections:
            self.active_connections[group_id] = {}

        if chat_id not in self.active_connections[group_id]:
            self.active_connections[group_id][chat_id] = []

        self.active_connections[group_id][chat_id].append(websocket)

    def disconnect(self, websocket, group_id: int, chat_id: int):
        if group_id in self.active_connections:
            self.active_connections[group_id][chat_id].remove(websocket)

            if not self.active_connections[group_id]:
                del self.active_connections[group_id]

    async def broadcast(self, message: str, group_id: int, chat_id: int, access_token: str):
        async with async_session_maker() as session:
            user = await TokenManager.get_user_by_token(session, token=access_token)
        
        async with async_session_maker() as session:
            await MessageMenager.add_message(session, user_id=user.id, chat_id=chat_id, message=message)
        for connection in self.active_connections[group_id][chat_id]:
            await connection.send_text(Server_to_websocket_data(message=message, name=user.name).model_dump_json())

    

manager = ConnectionManager()

@router.websocket("/{group_id}/{chat_id}")
async def websocket_endpoint(
    *,
    websocket: WebSocket,
    group_id: int,
    chat_id: int,
    token: Annotated[str | None, Query()] = None,
):
    await verify_token(token)
    await manager.connect(websocket, group_id, chat_id)
    try:
        while True:
            message = await websocket.receive_text()
            await manager.broadcast(message, group_id, chat_id, token)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket,group_id, chat_id)

@router.post("/create_group")
async def create_group(user: Annotated[User, Depends(get_current_active_user)], title: str, description: str):
    group = Group(title=title, description=description)
    group.users.append(user)
    async with async_session_maker() as session:
        group = await GroupManager.add(session, group)
    return {"status": status.HTTP_201_CREATED}

@router.get("/get_my_groups")
async def get_token(user: Annotated[User, Depends(get_current_active_user)]):
    async with async_session_maker() as session:
        groups = await UserManager.get_groups(session, user)
    return groups

@router.get("/get_group_chats")
async def get_group_chat(token: Annotated[str, Depends(get_token_cookie)], group_id: int):
    async with async_session_maker() as session:
        group = await GroupManager.get_one_by(session, id=group_id)
        chats = await GroupManager.get_chats(session, group=group)
    return chats

@router.get("/create_group_chat")
async def create_group_chat(token: Annotated[str, Depends(get_token_cookie)], title: str, group_id: int):
    async with async_session_maker() as session:
        group = await GroupManager.get_one_by(session, id=group_id)
    
    chat = Chat(title=title, group=group)
    async with async_session_maker() as session:
        chat = await ChatManager.add(session, chat)
    return {"status": status.HTTP_201_CREATED}

@router.get("/last_group_messages")
async def get_last_messages(token: Annotated[str, Depends(get_token_cookie)], group_id: int, chat_id: int):
    async with async_session_maker() as session:
        messages = await MessageMenager.get_messages(session, group_id, chat_id)
    return messages
