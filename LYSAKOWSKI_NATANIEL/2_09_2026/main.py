from datetime import datetime

from fastapi import FastAPI, Query

from app.models import BookmarkPublic, CreateBookmark
from app import service

app = FastAPI()


@app.get("/")
def root():
    return {"message": "hello bookmarks"}


@app.get("/fake-bookmark", response_model=BookmarkPublic)
def fake_bookmark():
    return BookmarkPublic(
        id="123",
        url="https://fastapi.tiangolo.com",
        title="FastAPI docs",
        tags=["fastapi", "python"],
        created_at=datetime.now(),
    )


@app.post("/bookmarks", response_model=BookmarkPublic, status_code=201)
def create_bookmark(data: CreateBookmark):
    return service.create_bookmark(data)


@app.get("/bookmarks", response_model=list[BookmarkPublic])
def list_bookmarks(tag: str | None = Query(None)):
    return service.list_bookmarks(tag=tag)
