from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime

class BookmarkCreate(BaseModel):
    url: HttpUrl
    title: str = Field(min_length=1, max_length=200)
    tags: list[str] = []


class BookmarkPublic(BookmarkCreate):
    id: int
    created_at: datetime