"""Pydantic schemas for the bookmarks service."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl


class BookmarkCreate(BaseModel):
    """Payload accepted when creating a new bookmark."""

    url: HttpUrl
    title: str = Field(min_length=1, max_length=200)
    tags: list[str] = Field(default_factory=list)


class BookmarkPublic(BaseModel):
    """Representation of a bookmark returned to clients."""

    id: UUID
    url: HttpUrl
    title: str = Field(min_length=1, max_length=200)
    tags: list[str] = Field(default_factory=list)
    created_at: datetime

    @classmethod
    def new(cls, data: BookmarkCreate) -> "BookmarkPublic":
        """Build a BookmarkPublic from a BookmarkCreate, assigning id/created_at."""
        return cls(
            id=uuid4(),
            url=data.url,
            title=data.title,
            tags=data.tags,
            created_at=datetime.now(timezone.utc),
        )
