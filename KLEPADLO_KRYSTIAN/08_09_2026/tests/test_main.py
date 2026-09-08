import pytest
from fastapi.testclient import TestClient
from app.main import app, service


@pytest.fixture(autouse=True)
def clean_store():
    service._store.clear()
    yield
    service._store.clear()


client = TestClient(app)


def test_create_bookmark_success():
    payload = {
        "url": "https://fastapi.tiangolo.com/",
        "title": "FastAPI Docs",
        "tags": ["docs", "python"],
    }
    response = client.post("/bookmarks", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["url"] == "https://fastapi.tiangolo.com/"
    assert data["title"] == "FastAPI Docs"
    assert "id" in data
    assert "created_at" in data


def test_create_bookmark_invalid_url():
    payload = {"url": "not-a-valid-url", "title": "Invalid"}
    response = client.post("/bookmarks", json=payload)
    assert response.status_code == 422


def test_create_bookmark_title_too_short():
    payload = {"url": "https://example.com", "title": ""}
    response = client.post("/bookmarks", json=payload)
    assert response.status_code == 422


def test_create_bookmark_title_too_long():
    payload = {"url": "https://example.com", "title": "A" * 201}
    response = client.post("/bookmarks", json=payload)
    assert response.status_code == 422


def test_get_bookmark_by_id_success():
    created = client.post(
        "/bookmarks", json={"url": "https://python.org", "title": "Python"}
    ).json()
    response = client.get(f"/bookmarks/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_bookmark_not_found():
    response = client.get("/bookmarks/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_filter_bookmarks_by_tag():
    client.post(
        "/bookmarks",
        json={
            "url": "https://a.com",
            "title": "A",
            "tags": ["python", "backend"],
        },
    )
    client.post(
        "/bookmarks",
        json={"url": "https://b.com", "title": "B", "tags": ["frontend"]},
    )

    response = client.get("/bookmarks?tag=backend")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "A"


def test_delete_bookmark_success():
    created = client.post(
        "/bookmarks", json={"url": "https://delete.me", "title": "Delete Me"}
    ).json()
    b_id = created["id"]

    del_resp = client.delete(f"/bookmarks/{b_id}")
    assert del_resp.status_code == 204

    fetch_resp = client.get(f"/bookmarks/{b_id}")
    assert fetch_resp.status_code == 404


def test_delete_bookmark_not_found():
    response = client.delete("/bookmarks/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404