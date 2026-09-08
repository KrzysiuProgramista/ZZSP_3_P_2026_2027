from datetime import datetime

from models import BookmarkCreate, BookmarkPublic

bookmarks: dict[int, BookmarkPublic] = {}
next_id = 1


def create(data: BookmarkCreate) -> BookmarkPublic:
    global next_id
    bookmark = BookmarkPublic(
        id=next_id, created_at=datetime.now(), **data.model_dump()
    )
    bookmarks[next_id] = bookmark
    next_id += 1
    return bookmark


def get_all(tag: str | None = None) -> list[BookmarkPublic]:
    if tag is None:
        return list(bookmarks.values())
    return [b for b in bookmarks.values() if tag in b.tags]


def get_one(bookmark_id: int) -> BookmarkPublic | None:
    return bookmarks.get(bookmark_id)


def delete(bookmark_id: int) -> bool:
    return bookmarks.pop(bookmark_id, None) is not None
