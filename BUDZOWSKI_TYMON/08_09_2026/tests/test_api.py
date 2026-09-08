import uuid

PAYLOAD = {
    "url": "https://fastapi.tiangolo.com/",
    "title": "FastAPI docs",
    "tags": ["python", "web"],
}


def make(client, **overrides):
    body = {**PAYLOAD, **overrides}
    response = client.post("/bookmarks", json=body)
    assert response.status_code == 201, response.text
    return response.json()


def test_create_returns_201_with_generated_fields(client):
    created = make(client)
    assert created["title"] == "FastAPI docs"
    assert created["url"] == "https://fastapi.tiangolo.com/"
    assert created["tags"] == ["python", "web"]
    uuid.UUID(created["id"])          # parses, so it is a real uuid
    assert created["created_at"]


def test_create_rejects_a_url_that_is_not_a_url(client):
    response = client.post("/bookmarks", json={**PAYLOAD, "url": "not-a-url"})
    assert response.status_code == 422


def test_create_rejects_empty_and_overlong_titles(client):
    assert client.post("/bookmarks", json={**PAYLOAD, "title": ""}).status_code == 422
    assert client.post("/bookmarks", json={**PAYLOAD, "title": "x" * 201}).status_code == 422
    assert client.post("/bookmarks", json={**PAYLOAD, "title": "x" * 200}).status_code == 201


def test_tags_default_to_an_empty_list(client):
    created = client.post(
        "/bookmarks", json={"url": "https://example.com", "title": "No tags"}
    ).json()
    assert created["tags"] == []


def test_tags_are_normalized_and_deduplicated(client):
    created = make(client, tags=["  Python ", "python", "", "Web"])
    assert created["tags"] == ["python", "web"]


def test_list_returns_everything_in_insertion_order(client):
    first = make(client, title="First")
    second = make(client, title="Second")

    response = client.get("/bookmarks")
    assert response.status_code == 200
    assert [b["id"] for b in response.json()] == [first["id"], second["id"]]


def test_list_filters_by_tag(client):
    python_one = make(client, title="Python one", tags=["python"])
    make(client, title="Rust one", tags=["rust"])

    response = client.get("/bookmarks", params={"tag": "python"})
    assert response.status_code == 200
    assert [b["id"] for b in response.json()] == [python_one["id"]]


def test_tag_filter_ignores_case_and_returns_empty_on_no_match(client):
    make(client, tags=["Python"])
    assert len(client.get("/bookmarks", params={"tag": "PYTHON"}).json()) == 1
    assert client.get("/bookmarks", params={"tag": "cobol"}).json() == []


def test_get_by_id_returns_the_same_bookmark(client):
    created = make(client)
    response = client.get(f"/bookmarks/{created['id']}")
    assert response.status_code == 200
    assert response.json() == created


def test_get_unknown_id_is_404_and_malformed_id_is_422(client):
    assert client.get(f"/bookmarks/{uuid.uuid4()}").status_code == 404
    assert client.get("/bookmarks/definitely-not-a-uuid").status_code == 422


def test_delete_removes_the_bookmark(client):
    created = make(client)
    response = client.delete(f"/bookmarks/{created['id']}")
    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/bookmarks/{created['id']}").status_code == 404
    assert client.get("/bookmarks").json() == []


def test_delete_twice_is_404_the_second_time(client):
    created = make(client)
    assert client.delete(f"/bookmarks/{created['id']}").status_code == 204
    assert client.delete(f"/bookmarks/{created['id']}").status_code == 404
