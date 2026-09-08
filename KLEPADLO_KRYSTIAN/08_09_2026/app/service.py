from uuid import UUID
from app.models import BookmarkCreate, BookmarkInternal, BookmarkPublic


class BookmarkNotFoundError(Exception):
    pass


class BookmarkService:

    def __init__(self) -> None:
        self._store: dict[UUID, BookmarkInternal] = {}

    def create(self, payload: BookmarkCreate) -> BookmarkPublic:
        bookmark = BookmarkInternal(**payload.model_dump())
        self._store[bookmark.id] = bookmark
        return BookmarkPublic(**bookmark.model_dump())

    def list_all(self, tag: str | None = None) -> list[BookmarkPublic]:
        records = self._store.values()
        if tag is not None:
            records = [b for b in records if tag in b.tags]
        return [BookmarkPublic(**b.model_dump()) for b in records]

    def get_by_id(self, bookmark_id: UUID) -> BookmarkPublic:
        bookmark = self._store.get(bookmark_id)
        if bookmark is None:
            raise BookmarkNotFoundError(
                f"Bookmark {bookmark_id} does not exist"
            )
        return BookmarkPublic(**bookmark.model_dump())

    def delete(self, bookmark_id: UUID) -> None:
        if bookmark_id not in self._store:
            raise BookmarkNotFoundError(
                f"Bookmark {bookmark_id} does not exist"
            )
        del self._store[bookmark_id]