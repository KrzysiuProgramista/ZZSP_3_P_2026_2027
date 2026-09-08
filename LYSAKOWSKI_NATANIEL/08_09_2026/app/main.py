from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response

from app.models import BookmarkPublic, CreateBookmark
from app import service

app = FastAPI()


@app.get("/")
def root():
    return {"message": "hello bookmarks"}


@app.post("/bookmarks", response_model=BookmarkPublic, status_code=201)
def create_bookmark(data: CreateBookmark):
    return service.create_bookmark(data)


@app.get("/bookmarks", response_model=list[BookmarkPublic])
def list_bookmarks(tag: str | None = Query(None)):
    return service.list_bookmarks(tag=tag)


@app.get("/bookmarks/{bookmark_id}", response_model=BookmarkPublic)
def get_bookmark(bookmark_id: str):
    bookmark = service.get_bookmark(bookmark_id)
    if bookmark is None:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return bookmark


@app.delete("/bookmarks/{bookmark_id}")
def delete_bookmark(bookmark_id: str):
    deleted = service.delete_bookmark(bookmark_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return Response(status_code=204)
