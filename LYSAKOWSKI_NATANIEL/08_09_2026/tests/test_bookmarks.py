import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    from app import storage
    storage.bookmarks_db.clear()

    with TestClient(app) as test_client:
        yield test_client

    storage.bookmarks_db.clear()


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "hello bookmarks"}


def test_create_bookmark_success(client):
    data = {
        "url": "https://fastapi.tiangolo.com",
        "title": "FastAPI docs",
        "tags": ["fastapi", "python"],
    }
    response = client.post("/bookmarks", json=data)
    assert response.status_code == 201
    body = response.json()
    assert body["url"] == "https://fastapi.tiangolo.com/"
    assert body["title"] == "FastAPI docs"
    assert body["tags"] == ["fastapi", "python"]
    assert "id" in body
    assert "created_at" in body


def test_create_bookmark_invalid_url(client):
    data = {
        "url": "not-a-url",
        "title": "Bad URL",
        "tags": [],
    }
    response = client.post("/bookmarks", json=data)
    assert response.status_code == 422  # validation error


def test_create_bookmark_title_too_long(client):
    data = {
        "url": "https://example.com",
        "title": "x" * 201,  # 201 chars, max is 200
        "tags": [],
    }
    response = client.post("/bookmarks", json=data)
    assert response.status_code == 422


def test_list_bookmarks_empty(client):
    response = client.get("/bookmarks")
    assert response.status_code == 200
    assert response.json() == []


def test_list_bookmarks_with_items(client):
    b1 = {
        "url": "https://example.com/1",
        "title": "First",
        "tags": ["python"],
    }
    b2 = {
        "url": "https://example.com/2",
        "title": "Second",
        "tags": ["fastapi"],
    }
    client.post("/bookmarks", json=b1)
    client.post("/bookmarks", json=b2)

    response = client.get("/bookmarks")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 2


def test_list_bookmarks_filter_by_tag(client):
    b1 = {
        "url": "https://example.com/1",
        "title": "Python stuff",
        "tags": ["python", "learning"],
    }
    b2 = {
        "url": "https://example.com/2",
        "title": "FastAPI stuff",
        "tags": ["fastapi", "learning"],
    }
    client.post("/bookmarks", json=b1)
    client.post("/bookmarks", json=b2)

    response = client.get("/bookmarks", params={"tag": "python"})
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["title"] == "Python stuff"

    response = client.get("/bookmarks", params={"tag": "learning"})
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 2


def test_get_bookmark_by_id_found(client):
    data = {
        "url": "https://example.com/1",
        "title": "Only one",
        "tags": ["test"],
    }
    create_resp = client.post("/bookmarks", json=data)
    assert create_resp.status_code == 201
    created = create_resp.json()
    bookmark_id = created["id"]

    response = client.get(f"/bookmarks/{bookmark_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == bookmark_id
    assert body["title"] == "Only one"


def test_get_bookmark_by_id_not_found(client):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/bookmarks/{fake_id}")
    assert response.status_code == 404
    assert "detail" in response.json()


def test_delete_bookmark_success(client):
    # Create a bookmark
    data = {
        "url": "https://example.com/to-delete",
        "title": "To Delete",
        "tags": ["temp"],
    }
    create_resp = client.post("/bookmarks", json=data)
    assert create_resp.status_code == 201
    created = create_resp.json()
    bookmark_id = created["id"]

    delete_resp = client.delete(f"/bookmarks/{bookmark_id}")
    assert delete_resp.status_code == 204

    get_resp = client.get(f"/bookmarks/{bookmark_id}")
    assert get_resp.status_code == 404


def test_delete_bookmark_not_found(client):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.delete(f"/bookmarks/{fake_id}")
    assert response.status_code == 404
    assert "detail" in response.json()
