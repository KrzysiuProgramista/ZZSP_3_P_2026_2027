from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query, status

from .models import BookmarkCreate, BookmarkPublic
from .repository import BookmarkRepository
from .service import BookmarkNotFoundError, BookmarkService

app = FastAPI(title="Bookmarks API")

repository = BookmarkRepository()
service = BookmarkService(repository)


def get_service() -> BookmarkService:
    return service


ServiceDependency = Annotated[BookmarkService, Depends(get_service)]


@app.post(
    "/bookmarks",
    response_model=BookmarkPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_bookmark(
    payload: BookmarkCreate,
    bookmark_service: ServiceDependency,
) -> BookmarkPublic:
    return bookmark_service.create(payload)


@app.get("/bookmarks", response_model=list[BookmarkPublic])
def list_bookmarks(
    bookmark_service: ServiceDependency,
    tag: str | None = Query(default=None),
) -> list[BookmarkPublic]:
    return bookmark_service.list_bookmarks(tag=tag)

@app.get("/bookmarks/{bookmark_id}", response_model=BookmarkPublic)
def get_bookmark(
    bookmark_id: UUID,
    bookmark_service: ServiceDependency,
) -> BookmarkPublic:
    try:
        return bookmark_service.get(bookmark_id)
    except BookmarkNotFoundError:
        raise HTTPException(status_code=404, detail="Bookmark not found")


@app.delete("/bookmarks/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bookmark(
    bookmark_id: UUID,
    bookmark_service: ServiceDependency,
) -> None:
    try:
        bookmark_service.delete(bookmark_id)
    except BookmarkNotFoundError:
        raise HTTPException(status_code=404, detail="Bookmark not found")