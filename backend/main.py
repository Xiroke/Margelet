from fastapi import FastAPI
import uvicorn
from admin import AdminAuth, add_views
from seed import seed_admin, seed_permissions, TestSeed
from database import create_db_and_tables, engine, get_async_session
from sqladmin import Admin
from config import settings

from auth.router import router as auth_router
from chat.router import router as chat_router
from chats.router import router as chats_router
from groups.router import router as group_router
from users.router import router as users_router

from fastapi.middleware.cors import CORSMiddleware
from auth.smtp import send_message
from bots.router import app as bots_app
import logging
from fastapi.staticfiles import StaticFiles


if settings.DEBUG:
	logging.basicConfig(
		level=logging.WARNING,
		format='%(asctime)s %(levelname)s %(message)s',
		handlers=[logging.FileHandler('log.log'), logging.StreamHandler()],
	)
else:
	logging.basicConfig(
		level=logging.WARNING,
		format='%(asctime)s %(levelname)s %(message)s',
		handlers=[logging.FileHandler('log.log')],
	)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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


app = FastAPI(
	debug=settings.DEBUG,
	openapi_url='/api/openapi.json',
	docs_url='/api/docs',
	redoc_url='/api/redoc',
)
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(chats_router)
app.include_router(group_router)
app.include_router(users_router)

app.mount(path='/api/bots', app=bots_app)
app.mount('/', StaticFiles(directory='static'), name='static')

app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,
	allow_credentials=True,
	allow_methods=['*'],
	allow_headers=['*'],
)


authentication_backend = AdminAuth(secret_key=settings.ADMIN_PANEL_SECRET)
admin = Admin(
	app=app,
	authentication_backend=authentication_backend,
	engine=engine,
	base_url='/api/admin',
)
add_views(admin)


@app.get('/api/ping')
async def get_ping():
	return 'pong'


@app.post('/api/ping')
async def post_ping(number: int):
	return number


@app.post('/api/send_email')
async def send_email():
	await send_message()
	return {'status': 'Email sent successfully!'}


@app.on_event('startup')
async def on_startup():
	await create_db_and_tables()

	logger.info('Start seeding...')
	async for session in get_async_session():
		await seed_permissions(session)
		admin = await seed_admin(session)
		group = await TestSeed.create_group(session, admin)
		await TestSeed.create_chats(session, group)
		await TestSeed.create_roles(session, group, admin)
		await TestSeed.create_messages(session, 1)
		await TestSeed.create_bot(session)
	logger.info('Seeding finished!')


if __name__ == '__main__':
	uvicorn.run('main:app', reload=True, port=8080)
