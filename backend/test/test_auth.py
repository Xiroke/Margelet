# from httpx import AsyncClient
# from config import settings
# from fastapi.testclient import TestClient
# from main import app
# import pytest
# from database import create_db_and_tables
# client = TestClient(app)

# # @pytest.fixture(scope='function')
# # def session():
# #     with async_session_maker() as session:
# #         yield session

# @pytest.fixture(scope='function')
# def create_db():
#     create_db_and_tables()

# def test_login():
#     data = {"username": "user@example.com", "password": "string"}
#     headers = {'Content-Type': 'application/x-www-form-urlencoded'}
#     response = client.post('/auth/jwt/login', data=data, headers=headers)
