import pytest
from app.api import chat as chat_router

@pytest.mark.asyncio
async def test_chat_query_stores_history(client, monkeypatch):
    register = {"name": "Chat User", "email": "chat.user@example.com", "password": "chatpass"}
    await client.post("/auth/register", json=register)
    auth_resp = await client.post("/auth/login", json={"email": register["email"], "password": register["password"]})
    token = auth_resp.json()["access_token"]

    async def fake_answer(question, document_ids, user_id):
        return "Test answer.", [{"document": "sample.pdf", "page": 1, "chunk_id": 1, "similarity": 0.98}]

    monkeypatch.setattr(chat_router, "answer_question", fake_answer)

    response = await client.post(
        "/chat/query",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "What is AI?", "document_ids": []},
    )
    assert response.status_code == 200
    assert response.json()["answer"] == "Test answer."
    assert response.json()["sources"][0]["document"] == "sample.pdf"
