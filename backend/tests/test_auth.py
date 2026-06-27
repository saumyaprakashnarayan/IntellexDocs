import pytest

@pytest.mark.asyncio
async def test_register_and_login(client):
    payload = {"name": "Test User", "email": "test.user@example.com", "password": "supersecret"}
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 200
    assert response.json()["email"] == payload["email"]

    response = await client.post("/auth/login", json={"email": payload["email"], "password": payload["password"]})
    assert response.status_code == 200
    json_data = response.json()
    assert "access_token" in json_data
    assert json_data["token_type"] == "bearer"
