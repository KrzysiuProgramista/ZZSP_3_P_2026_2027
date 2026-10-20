from datetime import datetime
from typing import List

from pydantic import BaseModel, HttpUrl, Field


class CreateBookmark(BaseModel):
    url: HttpUrl
    title: str = Field(..., min_length=1, max_length=200)
    tags: List[str] = []
    created_at: datetime | None = None


class BookmarkPublic(BaseModel):
    id: str
    url: HttpUrl
    title: str
    tags: List[str]
    created_at: datetime
