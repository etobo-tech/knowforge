from uuid import uuid4

from fastapi.testclient import TestClient


def test_create_list_get_update_and_append_message(client: TestClient) -> None:
    created = client.post("/api/chats", json={"title": "First chat"})
    assert created.status_code == 201
    chat_id = created.json()["id"]
    assert created.json()["title"] == "First chat"
    assert created.json()["messages"] == []

    second = client.post("/api/chats", json={"title": "Refund questions"})
    assert second.status_code == 201
    assert second.json()["title"] == "Refund questions"

    listed = client.get("/api/chats")
    assert listed.status_code == 200
    listed_ids = {item["id"] for item in listed.json()}
    assert len(listed_ids) == 2
    assert second.json()["id"] in listed_ids
    assert chat_id in listed_ids

    detail = client.get(f"/api/chats/{chat_id}")
    assert detail.status_code == 200

    patched = client.patch(
        f"/api/chats/{chat_id}",
        json={"title": "Updated title"},
    )
    assert patched.status_code == 200
    assert patched.json()["title"] == "Updated title"

    appended = client.post(
        f"/api/chats/{chat_id}/messages",
        json={"content": "What is the refund policy?"},
    )
    assert appended.status_code == 200
    messages = appended.json()["messages"]
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "What is the refund policy?"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == "Test reply to: What is the refund policy?"

    detail_after = client.get(f"/api/chats/{chat_id}")
    assert len(detail_after.json()["messages"]) == 2


def test_create_chat_requires_title(client: TestClient) -> None:
    assert client.post("/api/chats", json={}).status_code == 422
    assert client.post("/api/chats", json={"title": ""}).status_code == 422
    assert client.post("/api/chats", json={"title": "   "}).status_code == 422


def test_append_message_rejects_empty_content(client: TestClient) -> None:
    chat_id = client.post("/api/chats", json={"title": "Test chat"}).json()["id"]

    response = client.post(
        f"/api/chats/{chat_id}/messages",
        json={"content": "   "},
    )

    assert response.status_code == 400


def test_unknown_chat_returns_404(client: TestClient) -> None:
    unknown_id = uuid4()

    assert client.get(f"/api/chats/{unknown_id}").status_code == 404
    assert (
        client.patch(f"/api/chats/{unknown_id}", json={"title": "x"}).status_code == 404
    )
    assert (
        client.post(
            f"/api/chats/{unknown_id}/messages",
            json={"content": "hi"},
        ).status_code
        == 404
    )
