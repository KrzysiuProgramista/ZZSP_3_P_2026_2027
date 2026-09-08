from datetime import datetime
from .models import BookmarkCreate, BookmarkPublic

bookmarks = []
next_id = 1


def create_bookmark(data: BookmarkCreate) -> BookmarkPublic:
    global next_id

    bookmark = BookmarkPublic(
        id=next_id,
        created_at=datetime.now(),
        **data.model_dump()
    )

    bookmarks.append(bookmark)
    next_id += 1

    return bookmark


def get_bookmarks(tag: str | None = None) -> list[BookmarkPublic]:
    tagBookmarks = []
    if tag:
        for b in bookmarks:
            if tag in b.tags:
                tagBookmarks.append(b)
        return tagBookmarks

    return bookmarks


def get_bookmark(bookmark_id: int) -> BookmarkPublic | None:
    for bookmark in bookmarks:
        if bookmark.id == bookmark_id:
            return bookmark

    return None


def delete_bookmark(bookmark_id: int) -> bool:
    bookmark = get_bookmark(bookmark_id)

    if bookmark is None:
        return False

    bookmarks.remove(bookmark)
    return True