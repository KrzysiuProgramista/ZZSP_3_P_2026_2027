from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class BookmarkCreate(BaseModel):
    url: HttpUrl
    title: str = Field(min_length=1, max_length=200)
    tags: list[str] = Field(default_factory=list)




class BookmarkPublic(BookmarkCreate):
    id: UUID
    created_at: datetime
