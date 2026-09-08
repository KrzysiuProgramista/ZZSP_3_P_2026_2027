import uuid
from datetime import datetime, timezone
from typing import List

from app.models import CreateBookmark, BookmarkPublic
from app import storage


def create_bookmark(data: CreateBookmark) -> BookmarkPublic:
    bookmark_id = str(uuid.uuid4())

    if data.created_at is None:
        created_at = datetime.now(timezone.utc)
    else:
        created_at = data.created_at

    stored = {
        "id": bookmark_id,
        "url": str(data.url),
        "title": data.title,
        "tags": data.tags,
        "created_at": created_at,
    }

    storage.add_bookmark(bookmark_id, stored)

    return BookmarkPublic(**stored)


def list_bookmarks(tag: str | None = None) -> List[BookmarkPublic]:
    if tag is None:
        rows = storage.get_all_bookmarks()
    else:
        rows = storage.filter_bookmarks_by_tag(tag)

    return [BookmarkPublic(**row) for row in rows]


def get_bookmark(bookmark_id: str) -> BookmarkPublic | None:
    row = storage.get_bookmark_by_id(bookmark_id)
    if row is None:
        return None
    return BookmarkPublic(**row)


def delete_bookmark(bookmark_id: str) -> bool:
    return storage.delete_bookmark_by_id(bookmark_id)
