from fastapi import FastAPI, Depends
from typing import Annotated
import uvicorn
from admin import AdminAuth, add_views, admin_seed
from database import create_db_and_tables, engine
from sqladmin import Admin
from config import settings
from auth.router import router as auth_router
from chat.router import router as chat_router
from fastapi.middleware.cors import CORSMiddleware
from auth.utils import get_token_cookie

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:60",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:3000",
]


app = FastAPI(debug=settings.DEBUG, openapi_url="/api/openapi.json", docs_url="/api/docs", redoc_url="/api/redoc")

app.include_router(auth_router)
app.include_router(chat_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


authentication_backend = AdminAuth(secret_key=settings.ADMIN_PANEL_SECRET)
admin = Admin(app=app, authentication_backend=authentication_backend, engine=engine, base_url="/api/admin")
add_views(admin)



@app.get("/api/ping")
async def pong(token: Annotated[str, Depends(get_token_cookie)]):
    return 'pong'


@app.on_event("startup")
async def on_startup():
    # Not needed if you setup a migration system like Alembic
    await create_db_and_tables()
    await admin_seed()

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=8000)
