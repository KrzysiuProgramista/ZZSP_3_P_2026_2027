from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, HttpUrl


class BookmarkCreate(BaseModel):
    url: HttpUrl
    title: str = Field(min_length=1, max_length=200)
    tags: List[str]


class Bookmark(BaseModel):
    id: int
    url: HttpUrl
    title: str
    tags: List[str]
    created_at: datetime