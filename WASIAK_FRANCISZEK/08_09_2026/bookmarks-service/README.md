# ZZSP_3_P_2026_2027

# Bookmarks API

Small FastAPI service to manage bookmarks (URL, title, tags) with an in‑memory store.

## Features
## Features

- Create, list, get, filter, and delete bookmarks.
- Validates HTTP/HTTPS URLs and title length.
- Normalizes tags: trims whitespace, converts to lowercase, and removes duplicates/empty tags.
- Supports case-insensitive tag filtering.
- Returns bookmarks newest first.
- Uses a layered design: FastAPI routes → service → repository.
- Includes automated `TestClient` tests.
- Runs in Docker.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest          # run tests
uvicorn app.main:app --reload
```

Open: http://localhost:8000/docs

## Run with Docker

```bash
docker build -t bookmarks-api .
docker run --rm -p 8000:8000 bookmarks-api
```

If port 8000 is busy:

```bash
docker run --rm -p 8001:8000 bookmarks-api
```

Then: http://localhost:8001/docs

## Example requests

Create:

```bash
curl -X POST http://localhost:8000/bookmarks \
  -H "Content-Type: application/json" \
  -d '{"url":"[https://example.com](https://example.com)","title":"Example","tags":["test"]}'
```

List:

```bash
curl http://localhost:8000/bookmarks
curl "http://localhost:8000/bookmarks?tag=test"
```

Get / delete:

```bash
curl http://localhost:8000/bookmarks/<ID>
curl -X DELETE http://localhost:8000/bookmarks/<ID>
```