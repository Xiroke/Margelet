from fastapi import APIRouter, WebSocket, Query, Depends
from fastapi.websockets import WebSocketDisconnect
from typing import Annotated, Dict, List
from dao import ChatManager, TokenManager, MessageManager, UserGroupManager
from database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from auth.utils import get_current_active_user, verify_token
from .schemas import Server_to_client
from .schemas import AllLastMessages, ChatMessages
import json
from pydantic import ValidationError
from fastapi import HTTPException

router = APIRouter(prefix='/api/chat', tags=['chat'])


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
		self.active_connections: Dict[int,  List[WebSocket]] = {}  # {chat_id: [ws]}

	async def connect(self, websocket: WebSocket, chat_id: int):
		await websocket.accept()
		# create key chat_id if not exists
		if chat_id not in self.active_connections.keys():
			self.active_connections[chat_id] = []

		self.active_connections[chat_id].append(websocket)

	def disconnect(self, websocket, chat_id: int):
		self.active_connections[chat_id].remove(websocket)

	async def broadcast(
		self,
		text: str,
		chat_id: int,
		access_token: str,
		session: AsyncSession,
	):
		user = await TokenManager.get_user_by_token(session, token=access_token)
		message = await MessageManager.create_message(
			session, user_id=user.id, chat_id=chat_id, text=text
		)
		await session.commit()
		data = Server_to_client(
			id=message.id,
			local_id=message.local_id,
			text=text,
			name=user.name,
			chat_id=chat_id,
			created_at=message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
		)
		for connection in self.active_connections[chat_id]:
			await connection.send_text(data.model_dump_json())


connection_manager_users = ConnectionManager()


@router.websocket('/{chat_id}')
async def websocket_endpoint(
	session: Annotated[AsyncSession, Depends(get_async_session)],
	websocket: WebSocket,
	chat_id: int,
	token: Annotated[str | None, Query()] = None,
):
	await verify_token(token, session)
	await connection_manager_users.connect(websocket, chat_id)
	try:
		while True:
			text = await websocket.receive_text()
			await connection_manager_users.broadcast(
				text, chat_id, token, session
			)

	except WebSocketDisconnect:
		connection_manager_users.disconnect(websocket, chat_id)


@router.get('/chat_last_messages/{group_id}/{chat_id}')
async def chat_last_messages(
	user: Annotated[str, Depends(get_current_active_user)],
	session: Annotated[AsyncSession, Depends(get_async_session)],
	group_id: int,
	chat_id: int,
	last_message_local_id: int | List[int],
):
	# is User in Group
	await UserGroupManager.get_one_by(session, group_id=group_id, user_id=user.id)
	# is Chat in This Group
	await ChatManager.get_one_by(session, id=chat_id, group_id=group_id)

	messages = await MessageManager.get_chat_last_messages(
		session=session,
		chat_id=chat_id,
		last_message_local_id=last_message_local_id,
	)
	return messages


@router.get('/chat_all_last_messages')
async def chat_all_last_messages(
	user: Annotated[str, Depends(get_current_active_user)],
	session: Annotated[AsyncSession, Depends(get_async_session)],
	params: str,
):
	params = json.loads(params)

	chat_messages = []
	for item in params:
		try:
			item = AllLastMessages(**item)
		except ValidationError:
			raise HTTPException(status_code = 400)
		
		await UserGroupManager.get_one_by(
			session, group_id=item.group_id, user_id=user.id
		)
		await ChatManager.get_one_by(session, id=item.chat_id, group_id=item.group_id)
		messages = await MessageManager.get_chat_last_messages(
			session=session,
			chat_id=item.chat_id,
			last_message_local_id=item.last_message_local_id,
		)
		if messages:
			chat_messages.append(
				ChatMessages(
					group_id=item.group_id,
					chat_id=item.chat_id,
					messages=messages,
				)
			)

	return chat_messages
