"""Pydantic models for bookmarks."""

from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, field_validator


def _now() -> datetime:
    return datetime.now(timezone.utc)


class BookmarkCreate(BaseModel):
    """What a client sends when creating a bookmark."""

    url: HttpUrl
    title: str = Field(min_length=1, max_length=200)
    tags: list[str] = Field(default_factory=list)

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("title must not be blank")
        return stripped

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, values: list[str]) -> list[str]:
        """Lowercase, trim, drop empties, keep first occurrence of each tag."""
        seen: list[str] = []
        for tag in values:
            tag = tag.strip().lower()
            if tag and tag not in seen:
                seen.append(tag)
        return seen


class BookmarkPublic(BookmarkCreate):
    """What the API gives back."""

    id: UUID
    created_at: datetime = Field(default_factory=_now)
