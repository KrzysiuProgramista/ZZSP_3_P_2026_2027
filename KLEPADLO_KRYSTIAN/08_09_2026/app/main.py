from uuid import UUID
from fastapi import FastAPI, HTTPException, Query, status
from app.models import BookmarkCreate, BookmarkPublic
from app.service import BookmarkNotFoundError, BookmarkService

app = FastAPI(title="Bookmarks Service")
service = BookmarkService()


@app.post(
    "/bookmarks",
    response_model=BookmarkPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_bookmark(payload: BookmarkCreate) -> BookmarkPublic:
    return service.create(payload)


@app.get("/bookmarks", response_model=list[BookmarkPublic])
def get_bookmarks(tag: str | None = Query(default=None)) -> list[BookmarkPublic]:
    return service.list_all(tag=tag)


@app.get("/bookmarks/{bookmark_id}", response_model=BookmarkPublic)
def get_bookmark(bookmark_id: UUID) -> BookmarkPublic:
    try:
        return service.get_by_id(bookmark_id)
    except BookmarkNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@app.delete("/bookmarks/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bookmark(bookmark_id: UUID) -> None:
    try:
        service.delete(bookmark_id)
    except BookmarkNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )