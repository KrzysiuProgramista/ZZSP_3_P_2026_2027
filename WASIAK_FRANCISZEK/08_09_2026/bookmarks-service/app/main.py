from uuid import UUID

from fastapi import FastAPI, HTTPException, Query, status

from .models import BookmarkCreate, BookmarkPublic
from .service import BookmarkNotFoundError, BookmarkService

app = FastAPI(title="Bookmarks API")
service = BookmarkService()


@app.post(
    "/bookmarks",
    response_model=BookmarkPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_bookmark(payload: BookmarkCreate) -> BookmarkPublic:
    return service.create(payload)


@app.get("/bookmarks", response_model=list[BookmarkPublic])
def list_bookmarks(tag: str | None = Query(default=None)) -> list[BookmarkPublic]:
    return service.list(tag=tag)


@app.get("/bookmarks/{bookmark_id}", response_model=BookmarkPublic)
def get_bookmark(bookmark_id: UUID) -> BookmarkPublic:
    try:
        return service.get(bookmark_id)
    except BookmarkNotFoundError:
        raise HTTPException(status_code=404, detail="Bookmark not found")


@app.delete("/bookmarks/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bookmark(bookmark_id: UUID) -> None:
    try:
        service.delete(bookmark_id)
    except BookmarkNotFoundError:
        raise HTTPException(status_code=404, detail="Bookmark not found")
