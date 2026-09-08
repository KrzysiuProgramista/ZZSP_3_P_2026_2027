import pytest
from fastapi.testclient import TestClient

from app.main import app, get_service
from app.repository import BookmarkRepository
from app.service import BookmarkService


@pytest.fixture(autouse=True)
def reset_service() -> None:
    test_service = BookmarkService(BookmarkRepository())
    app.dependency_overrides[get_service] = lambda: test_service

    yield

    app.dependency_overrides.clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def valid_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "url": "https://example.com/article",
        "title": "Example article",
        "tags": ["python", "reading"],
    }
    payload.update(overrides)
    return payload


def test_create_bookmark_returns_201_and_public_fields(client: TestClient) -> None:
    response = client.post("/bookmarks", json=valid_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["url"] == "https://example.com/article"
    assert body["title"] == "Example article"
    assert body["tags"] == ["python", "reading"]
    assert "id" in body
    assert "created_at" in body


def test_create_defaults_tags_to_empty_list(client: TestClient) -> None:
    response = client.post(
        "/bookmarks",
        json={"url": "https://example.com", "title": "No tags"},
    )

    assert response.status_code == 201
    assert response.json()["tags"] == []


def test_create_normalizes_tags(client: TestClient) -> None:
    response = client.post(
        "/bookmarks",
        json=valid_payload(tags=[" Python ", "python", "", "API ", "api"]),
    )

    assert response.status_code == 201
    assert response.json()["tags"] == ["python", "api"]


def test_create_rejects_non_http_url(client: TestClient) -> None:
    response = client.post("/bookmarks", json=valid_payload(url="ftp://example.com"))

    assert response.status_code == 422


def test_create_rejects_empty_title(client: TestClient) -> None:
    response = client.post("/bookmarks", json=valid_payload(title=""))

    assert response.status_code == 422


def test_create_rejects_title_longer_than_200_characters(client: TestClient) -> None:
    response = client.post("/bookmarks", json=valid_payload(title="x" * 201))

    assert response.status_code == 422


def test_list_returns_all_bookmarks(client: TestClient) -> None:
    client.post("/bookmarks", json=valid_payload(title="First"))
    client.post("/bookmarks", json=valid_payload(title="Second"))

    response = client.get("/bookmarks")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_filters_case_insensitively_by_tag(client: TestClient) -> None:
    client.post("/bookmarks", json=valid_payload(title="Python", tags=["Python"]))
    client.post("/bookmarks", json=valid_payload(title="FastAPI", tags=["fastapi"]))

    response = client.get("/bookmarks", params={"tag": " PYTHON "})

    assert response.status_code == 200
    assert [bookmark["title"] for bookmark in response.json()] == ["Python"]


def test_list_returns_newest_bookmark_first(client: TestClient) -> None:
    client.post("/bookmarks", json=valid_payload(title="Older"))
    client.post("/bookmarks", json=valid_payload(title="Newer"))

    response = client.get("/bookmarks")

    assert response.status_code == 200
    assert [bookmark["title"] for bookmark in response.json()] == ["Newer", "Older"]


def test_get_bookmark_returns_existing_bookmark(client: TestClient) -> None:
    created = client.post("/bookmarks", json=valid_payload()).json()

    response = client.get(f"/bookmarks/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_missing_bookmark_returns_404(client: TestClient) -> None:
    response = client.get("/bookmarks/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    assert response.json()["detail"] == "Bookmark not found"


def test_delete_bookmark_removes_it(client: TestClient) -> None:
    created = client.post("/bookmarks", json=valid_payload()).json()

    delete_response = client.delete(f"/bookmarks/{created['id']}")
    get_response = client.get(f"/bookmarks/{created['id']}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


def test_delete_missing_bookmark_returns_404(client: TestClient) -> None:
    response = client.delete("/bookmarks/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404