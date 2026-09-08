from fastapi import FastAPI
from Service import BookmarkService, Bookmark
from typing import Optional

app = FastAPI()
Service = BookmarkService()

@app.get("/bookmarks")
async def GetBookmarks(tag: Optional[str] = "") -> list[Bookmark]:
    return await Service.GetBookmarks(tag)

@app.get("/bookmarks/{id}") 
async def GetBookmark(id: int) -> Bookmark | bool:
    return await Service.GetBookmarkByID(id)

@app.post("/bookmarks")
async def AddBookmark(NewBookmark: Bookmark) -> bool:
    return await Service.AddBookmark(NewBookmark)

@app.delete("/bookmarks/{id}")
async def RemoveBookmarkByID(id: int) -> bool:
    return await Service.RemoveBookmark(id)
