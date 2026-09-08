from datetime import datetime, timezone
from uuid import UUID, uuid4

from .models import BookmarkCreate, BookmarkPublic
from .repository import BookmarkRepository


class BookmarkNotFoundError(Exception):
    pass


class BookmarkService:
    def __init__(self, repository: BookmarkRepository) -> None:
        self._repository = repository

    def create(self, payload: BookmarkCreate) -> BookmarkPublic:
        cleaned_tags = self._clean_tags(payload.tags)

        bookmark = BookmarkPublic(
            id=uuid4(),
            url=payload.url,
            title=payload.title,
            tags=cleaned_tags,
            created_at=datetime.now(timezone.utc),
        )

        return self._repository.add(bookmark)

    def list_bookmarks(self, tag: str | None = None) -> list[BookmarkPublic]:
        bookmarks = self._repository.list_all()

        if tag is not None:
            normalized_tag = tag.strip().lower()
            bookmarks = [
                bookmark
                for bookmark in bookmarks
                if normalized_tag in bookmark.tags
            ]

        return sorted(bookmarks, key=lambda bookmark: bookmark.created_at, reverse=True)

    def get(self, bookmark_id: UUID) -> BookmarkPublic:
        bookmark = self._repository.find_by_id(bookmark_id)

        if bookmark is None:
            raise BookmarkNotFoundError(str(bookmark_id))

        return bookmark

    def delete(self, bookmark_id: UUID) -> None:
        deleted = self._repository.remove_by_id(bookmark_id)

        if not deleted:
            raise BookmarkNotFoundError(str(bookmark_id))

    @staticmethod
    def _clean_tags(tags: list[str]) -> list[str]:
        cleaned: list[str] = []

        for tag in tags:
            normalized = tag.strip().lower()

            if normalized and normalized not in cleaned:
                cleaned.append(normalized)

        return cleaned# rebuild trigger
