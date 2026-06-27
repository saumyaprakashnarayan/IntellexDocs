import pytest
from app.api import documents as documents_router
from pypdf import PdfWriter
from io import BytesIO

@pytest.mark.asyncio
async def test_document_upload_and_list(client, monkeypatch):
    register = {"name": "Uploader", "email": "upload.user@example.com", "password": "securepass"}
    await client.post("/auth/register", json=register)
    auth_resp = await client.post("/auth/login", json={"email": register["email"], "password": register["password"]})
    token = auth_resp.json()["access_token"]

    async def dummy_ingest(*args, **kwargs):
        return None

    monkeypatch.setattr(documents_router, "ingest_document", dummy_ingest)

    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    buffer = BytesIO()
    writer.write(buffer)
    buffer.seek(0)

    response = await client.post(
        "/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("test.pdf", buffer.getvalue(), "application/pdf")},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Upload successful."

    list_response = await client.get("/documents/", headers={"Authorization": f"Bearer {token}"})
    assert list_response.status_code == 200
    assert isinstance(list_response.json(), list)
