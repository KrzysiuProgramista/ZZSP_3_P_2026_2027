"""In-memory service layer for bookmarks.

Deliberately free of any FastAPI imports so it can be tested and reused
independently of the web framework.
"""
from __future__ import annotations

from threading import Lock
from uuid import UUID

from app.models import BookmarkCreate, BookmarkPublic


class BookmarkNotFoundError(Exception):
    """Raised when a bookmark with the given id does not exist."""

    def __init__(self, bookmark_id: UUID):
        self.bookmark_id = bookmark_id
        super().__init__(f"Bookmark {bookmark_id} not found")


class BookmarkStore:
    """A simple thread-safe in-memory store for bookmarks."""

    def __init__(self) -> None:
        self._bookmarks: dict[UUID, BookmarkPublic] = {}
        self._lock = Lock()

    def create(self, data: BookmarkCreate) -> BookmarkPublic:
        bookmark = BookmarkPublic.new(data)
        with self._lock:
            self._bookmarks[bookmark.id] = bookmark
        return bookmark

    def list(self, tag: str | None = None) -> list[BookmarkPublic]:
        with self._lock:
            bookmarks = list(self._bookmarks.values())
        if tag is not None:
            bookmarks = [b for b in bookmarks if tag in b.tags]
        return sorted(bookmarks, key=lambda b: b.created_at)

    def get(self, bookmark_id: UUID) -> BookmarkPublic:
        with self._lock:
            bookmark = self._bookmarks.get(bookmark_id)
        if bookmark is None:
            raise BookmarkNotFoundError(bookmark_id)
        return bookmark

    def delete(self, bookmark_id: UUID) -> None:
        with self._lock:
            if bookmark_id not in self._bookmarks:
                raise BookmarkNotFoundError(bookmark_id)
            del self._bookmarks[bookmark_id]

    def clear(self) -> None:
        """Remove all bookmarks. Handy for test isolation."""
        with self._lock:
            self._bookmarks.clear()


# Module-level default store used by the API layer.
store = BookmarkStore()
