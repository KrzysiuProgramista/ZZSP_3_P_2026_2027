# Bookmarks API

Small FastAPI service for storing bookmarks in memory.

## Endpoints

| Method | Path               | Notes                                   |
| ------ | ------------------ | --------------------------------------- |
| POST   | `/bookmarks`       | 201 + the created bookmark              |
| GET    | `/bookmarks`       | optional `?tag=` filter (case-insensitive) |
| GET    | `/bookmarks/{id}`  | 404 if the id is unknown                |
| DELETE | `/bookmarks/{id}`  | 204 on success, 404 if unknown          |

## Layout

- `app/models.py` — `BookmarkCreate` / `BookmarkPublic` (`HttpUrl`, title 1-200, tags, `created_at`)
- `app/service.py` — storage and lookup, no FastAPI imports
- `app/main.py` — routes only
- `tests/` — TestClient tests plus service-level tests

## Run locally

```sh
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

## Tests

```sh
pytest
```

## Docker

```sh
docker build -t bookmarks-api .
docker run --rm -p 8000:8000 bookmarks-api
curl -X POST localhost:8000/bookmarks \
  -H 'content-type: application/json' \
  -d '{"url":"https://example.com","title":"Example","tags":["demo"]}'
```
