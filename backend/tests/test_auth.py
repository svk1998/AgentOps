import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient):
    # Register
    res = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "secret123",
        "full_name": "Test User",
    })
    assert res.status_code == 201
    assert res.json()["email"] == "test@example.com"

    # Login
    res = await client.post("/api/v1/auth/login", data={
        "username": "test@example.com",
        "password": "secret123",
    })
    assert res.status_code == 200
    assert "access_token" in res.json()


@pytest.mark.asyncio
async def test_me(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "email": "me@example.com",
        "password": "secret123",
    })
    login = await client.post("/api/v1/auth/login", data={
        "username": "me@example.com",
        "password": "secret123",
    })
    token = login.json()["access_token"]

    res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["email"] == "me@example.com"
