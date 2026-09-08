from fastapi import FastAPI, HTTPException
from .models import BookmarkCreate
from .service import (
    create_bookmark,
    get_bookmarks,
    get_bookmark,
    delete_bookmark,
)

app = FastAPI()


@app.post("/bookmarks")
def create(data: BookmarkCreate):
    return create_bookmark(data)


@app.get("/bookmarks")
def get_all(tag: str | None = None):
    return get_bookmarks(tag)


@app.get("/bookmarks/{id}")
def get_one(id: int):
    bookmark = get_bookmark(id)

    if bookmark is None:
        raise HTTPException(404, "Bookmark not found")

    return bookmark


@app.delete("/bookmarks/{id}")
def delete(id: int):
    if not delete_bookmark(id):
        raise HTTPException(404, "Bookmark not found")

    return {"message": "Deleted"}
