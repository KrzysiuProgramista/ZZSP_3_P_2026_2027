from uuid import UUID

from .models import BookmarkPublic


class BookmarkRepository:
    def __init__(self) -> None:
        self._items: list[BookmarkPublic] = []

    def add(self, bookmark: BookmarkPublic) -> BookmarkPublic:
        self._items.append(bookmark)
        return bookmark

    def list_all(self) -> list[BookmarkPublic]:
        return list(self._items)

    def find_by_id(self, bookmark_id: UUID) -> BookmarkPublic | None:
        for bookmark in self._items:
            if bookmark.id == bookmark_id:
                return bookmark
        return None

    def remove_by_id(self, bookmark_id: UUID) -> bool:
        for index, bookmark in enumerate(self._items):
            if bookmark.id == bookmark_id:
                del self._items[index]
                return True
        return False