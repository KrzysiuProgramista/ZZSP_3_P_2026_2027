"""Bookmark storage and lookup. No FastAPI in here on purpose."""

from uuid import UUID, uuid4

from app.models import BookmarkCreate, BookmarkPublic


class BookmarkNotFound(LookupError):
    """Raised when an id does not match any stored bookmark."""

    def __init__(self, bookmark_id: UUID) -> None:
        super().__init__(f"bookmark {bookmark_id} not found")
        self.bookmark_id = bookmark_id


class BookmarkService:
    """In-memory bookmark store, insertion ordered."""

    def __init__(self) -> None:
        self._items: dict[UUID, BookmarkPublic] = {}

    def add(self, data: BookmarkCreate) -> BookmarkPublic:
        bookmark = BookmarkPublic(id=uuid4(), **data.model_dump())
        self._items[bookmark.id] = bookmark
        return bookmark

    def list(self, tag: str | None = None) -> list[BookmarkPublic]:
        items = list(self._items.values())
        if tag is None:
            return items
        wanted = tag.strip().lower()
        return [b for b in items if wanted in b.tags]

    def get(self, bookmark_id: UUID) -> BookmarkPublic:
        try:
            return self._items[bookmark_id]
        except KeyError:
            raise BookmarkNotFound(bookmark_id) from None

    def delete(self, bookmark_id: UUID) -> None:
        if self._items.pop(bookmark_id, None) is None:
            raise BookmarkNotFound(bookmark_id)

    def clear(self) -> None:
        self._items.clear()
