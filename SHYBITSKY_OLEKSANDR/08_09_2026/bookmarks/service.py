from datetime import datetime, timezone
from typing import Optional
from models import Bookmark, BookmarkCreate


class BookmarkService:
    def __init__(self):
        self.bookmarks: dict[int, Bookmark] = {}
        self.next_id = 1

    def create(self, data: BookmarkCreate) -> Bookmark:
        bookmark = Bookmark(
            id=self.next_id,
            url=data.url,
            title=data.title,
            tags=data.tags,
            created_at=datetime.now(),
        )

        self.bookmarks[self.next_id] = bookmark
        self.next_id += 1

        return bookmark

    def get_all(self, tag: Optional[str]) -> list[Bookmark]:
        if tag is None:
            return list(self.bookmarks.values())

        return [bookmark for bookmark in self.bookmarks.values() if tag in bookmark.tags]

    def get(self, bookmark_id: int) -> Optional[Bookmark]:
        return self.bookmarks.get(bookmark_id)

    def delete(self, bookmark_id: int) -> bool:
        if bookmark_id not in self.bookmarks:
            return False

        del self.bookmarks[bookmark_id]
        return True