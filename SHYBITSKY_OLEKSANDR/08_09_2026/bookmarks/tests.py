from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_bookmark():
    response = client.post(
        "/bookmarks",
        json={
            "url": "https://example.com",
            "title": "Example",
            "tags": ["python"],
        },
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Example"


def test_create_invalid_url():
    response = client.post(
        "/bookmarks",
        json={
            "url": "not-a-url",
            "title": "Example",
            "tags": [],
        },
    )
    assert response.status_code == 422


def test_create_empty_title():
    response = client.post(
        "/bookmarks",
        json={
            "url": "https://example.com",
            "title": "",
            "tags": [],
        },
    )
    assert response.status_code == 422


def test_get_bookmarks():
    response = client.get("/bookmarks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_filter_bookmarks_by_tag():
    client.post(
        "/bookmarks",
        json={
            "url": "https://python.org",
            "title": "Python",
            "tags": ["python"],
        },
    )
    response = client.get("/bookmarks?tag=python")
    assert response.status_code == 200
    for bookmark in response.json():
        assert "python" in bookmark["tags"]


def test_get_bookmark_by_id():
    create_response = client.post(
        "/bookmarks",
        json={
            "url": "https://github.com",
            "title": "GitHub",
            "tags": ["git"],
        },
    )
    bookmark_id = create_response.json()["id"]
    response = client.get(f"/bookmarks/{bookmark_id}")
    assert response.status_code == 200
    assert response.json()["id"] == bookmark_id


def test_get_nonexistent_bookmark():
    response = client.get("/bookmarks/999999")
    assert response.status_code == 404


def test_delete_bookmark():
    create_response = client.post(
        "/bookmarks",
        json={
            "url": "https://example.com/delete",
            "title": "Delete me",
            "tags": [],
        },
    )
    bookmark_id = create_response.json()["id"]
    response = client.delete(f"/bookmarks/{bookmark_id}")
    assert response.status_code == 200
    response = client.get(f"/bookmarks/{bookmark_id}")
    assert response.status_code == 404