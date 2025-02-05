import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_register_user():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/register/", json={"username": "testuser", "password": "testpass", "role": "owner"})
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

@pytest.mark.asyncio
async def test_login():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/login/", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_analyze_code():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/analyze/", json={"code": "print('Hello')"})
    assert response.status_code == 200
    assert "task_id" in response.json()
