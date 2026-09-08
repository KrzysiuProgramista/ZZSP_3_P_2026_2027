from datetime import datetime, timezone
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, HttpUrl


class BookmarkCreate(BaseModel):
    url: HttpUrl
    title: str = Field(min_length=1, max_length=200)
    tags: list[str] = Field(default_factory=list)


class BookmarkPublic(BaseModel):
    id: UUID
    url: HttpUrl
    title: str
    tags: list[str]
    created_at: datetime


class BookmarkInternal(BookmarkCreate):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )