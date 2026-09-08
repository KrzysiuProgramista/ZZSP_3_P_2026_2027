from collections.abc import Iterable
from datetime import datetime, timezone
from uuid import UUID, uuid4

from .models import BookmarkCreate, BookmarkPublic


class BookmarkNotFoundError(Exception):
    pass


class BookmarkService:
    def __init__(self) -> None:
        self._bookmarks: dict[UUID, BookmarkPublic] = {}

    def create(self, payload: BookmarkCreate) -> BookmarkPublic:
        bookmark = BookmarkPublic(
            id=uuid4(),
            created_at=datetime.now(timezone.utc),
            **payload.model_dump(),
        )
        self._bookmarks[bookmark.id] = bookmark
        return bookmark

    def list(self, tag: str | None = None) -> list[BookmarkPublic]:
        bookmarks: Iterable[BookmarkPublic] = self._bookmarks.values()
        if tag is not None:
            bookmarks = (b for b in bookmarks if tag in b.tags)
        return sorted(bookmarks, key=lambda b: b.created_at)

    def get(self, bookmark_id: UUID) -> BookmarkPublic:
        try:
            return self._bookmarks[bookmark_id]
        except KeyError:
            raise BookmarkNotFoundError(str(bookmark_id))

    def delete(self, bookmark_id: UUID) -> None:
        if bookmark_id not in self._bookmarks:
            raise BookmarkNotFoundError(str(bookmark_id))
        del self._bookmarks[bookmark_id]
