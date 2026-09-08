"""HTTP layer: routes only, all the work lives in the service."""

from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query, status

from app.models import BookmarkCreate, BookmarkPublic
from app.service import BookmarkNotFound, BookmarkService

app = FastAPI(title="Bookmarks API", version="1.0.0")

_service = BookmarkService()


def get_service() -> BookmarkService:
    return _service


@app.post("/bookmarks", response_model=BookmarkPublic, status_code=status.HTTP_201_CREATED)
def create_bookmark(
    payload: BookmarkCreate,
    service: BookmarkService = Depends(get_service),
) -> BookmarkPublic:
    return service.add(payload)


@app.get("/bookmarks", response_model=list[BookmarkPublic])
def list_bookmarks(
    tag: str | None = Query(default=None, description="only bookmarks carrying this tag"),
    service: BookmarkService = Depends(get_service),
) -> list[BookmarkPublic]:
    return service.list(tag)


@app.get("/bookmarks/{bookmark_id}", response_model=BookmarkPublic)
def read_bookmark(
    bookmark_id: UUID,
    service: BookmarkService = Depends(get_service),
) -> BookmarkPublic:
    try:
        return service.get(bookmark_id)
    except BookmarkNotFound as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc


@app.delete("/bookmarks/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bookmark(
    bookmark_id: UUID,
    service: BookmarkService = Depends(get_service),
) -> None:
    try:
        service.delete(bookmark_id)
    except BookmarkNotFound as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
