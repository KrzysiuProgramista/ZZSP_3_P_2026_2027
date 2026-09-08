import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.service import store


@pytest.fixture(autouse=True)
def clear_store():
    """Ensure each test starts with an empty bookmark store."""
    store.clear()
    yield
    store.clear()


@pytest.fixture
def client():
    return TestClient(app)


def make_payload(**overrides):
    payload = {
        "url": "https://example.com/article",
        "title": "Example Article",
        "tags": ["reading", "tech"],
    }
    payload.update(overrides)
    return payload


def test_create_bookmark_returns_201_and_full_object(client):
    response = client.post("/bookmarks", json=make_payload())
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Example Article"
    assert body["url"] == "https://example.com/article"
    assert body["tags"] == ["reading", "tech"]
    assert "id" in body
    assert "created_at" in body


def test_create_bookmark_rejects_invalid_url(client):
    response = client.post("/bookmarks", json=make_payload(url="not-a-url"))
    assert response.status_code == 422


def test_create_bookmark_rejects_empty_title(client):
    response = client.post("/bookmarks", json=make_payload(title=""))
    assert response.status_code == 422


def test_create_bookmark_rejects_title_over_200_chars(client):
    response = client.post("/bookmarks", json=make_payload(title="x" * 201))
    assert response.status_code == 422


def test_create_bookmark_defaults_tags_to_empty_list(client):
    payload = make_payload()
    del payload["tags"]
    response = client.post("/bookmarks", json=payload)
    assert response.status_code == 201
    assert response.json()["tags"] == []


def test_list_bookmarks_empty_initially(client):
    response = client.get("/bookmarks")
    assert response.status_code == 200
    assert response.json() == []


def test_list_bookmarks_returns_created_items(client):
    client.post("/bookmarks", json=make_payload(title="One"))
    client.post("/bookmarks", json=make_payload(title="Two"))
    response = client.get("/bookmarks")
    assert response.status_code == 200
    titles = {b["title"] for b in response.json()}
    assert titles == {"One", "Two"}


def test_list_bookmarks_filters_by_tag(client):
    client.post("/bookmarks", json=make_payload(title="Tech", tags=["tech"]))
    client.post("/bookmarks", json=make_payload(title="Cooking", tags=["food"]))
    response = client.get("/bookmarks", params={"tag": "tech"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "Tech"


def test_get_bookmark_by_id(client):
    created = client.post("/bookmarks", json=make_payload()).json()
    response = client.get(f"/bookmarks/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_bookmark_missing_returns_404(client):
    response = client.get("/bookmarks/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_delete_bookmark_removes_it(client):
    created = client.post("/bookmarks", json=make_payload()).json()
    delete_response = client.delete(f"/bookmarks/{created['id']}")
    assert delete_response.status_code == 204
    get_response = client.get(f"/bookmarks/{created['id']}")
    assert get_response.status_code == 404


def test_delete_bookmark_missing_returns_404(client):
    response = client.delete("/bookmarks/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
