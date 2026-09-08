from fastapi import FastAPI, HTTPException

import service
from models import BookmarkCreate, BookmarkPublic

app = FastAPI()


@app.post("/bookmarks", status_code=201)
def create(data: BookmarkCreate) -> BookmarkPublic:
    return service.create(data)


@app.get("/bookmarks")
def get_all(tag: str | None = None) -> list[BookmarkPublic]:
    return service.get_all(tag)


@app.get("/bookmarks/{bookmark_id}")
def get_one(bookmark_id: int) -> BookmarkPublic:
    bookmark = service.get_one(bookmark_id)
    if bookmark is None:
        raise HTTPException(404, "Bookmark not found")
    return bookmark


@app.delete("/bookmarks/{bookmark_id}", status_code=204)
def delete(bookmark_id: int) -> None:
    if not service.delete(bookmark_id):
        raise HTTPException(404, "Bookmark not found")
