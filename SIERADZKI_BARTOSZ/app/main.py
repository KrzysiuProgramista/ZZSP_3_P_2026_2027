"""FastAPI application exposing the bookmarks API."""
from __future__ import annotations

from uuid import UUID

from fastapi import FastAPI, HTTPException, status

from app.models import BookmarkCreate, BookmarkPublic
from app.service import BookmarkNotFoundError, store

app = FastAPI(title="bookmarks", version="1.0.0")


@app.post("/bookmarks", response_model=BookmarkPublic, status_code=status.HTTP_201_CREATED)
def create_bookmark(data: BookmarkCreate) -> BookmarkPublic:
    return store.create(data)


@app.get("/bookmarks", response_model=list[BookmarkPublic])
def list_bookmarks(tag: str | None = None) -> list[BookmarkPublic]:
    return store.list(tag=tag)


@app.get("/bookmarks/{bookmark_id}", response_model=BookmarkPublic)
def get_bookmark(bookmark_id: UUID) -> BookmarkPublic:
    try:
        return store.get(bookmark_id)
    except BookmarkNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")


@app.delete("/bookmarks/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bookmark(bookmark_id: UUID) -> None:
    try:
        store.delete(bookmark_id)
    except BookmarkNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")
