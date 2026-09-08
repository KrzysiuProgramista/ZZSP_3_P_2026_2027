from fastapi import FastAPI, HTTPException
from typing import Optional
from models import BookmarkCreate
from service import BookmarkService


app = FastAPI()

service = BookmarkService()


@app.post("/bookmarks")
def create_bookmark(body: BookmarkCreate):
    return service.create(body)


@app.get("/bookmarks")
def get_bookmarks(tag: Optional[str] = None):
    return service.get_all(tag)


@app.get("/bookmarks/{bookmark_id}") 
def get_bookmark(bookmark_id: int):
    bookmark = service.get(bookmark_id)

    if bookmark is None:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    return bookmark


@app.delete("/bookmarks/{bookmark_id}")
def delete_bookmark(bookmark_id: int):
    deleted = service.delete(bookmark_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    return {"message": "Bookmark deleted"}