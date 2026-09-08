from typing import Dict, List, Any


bookmarks_db: Dict[str, Dict[str, Any]] = {}


def add_bookmark(bookmark_id: str, data: Dict[str, Any]) -> None:
    bookmarks_db[bookmark_id] = data


def get_all_bookmarks() -> List[Dict[str, Any]]:
    return list(bookmarks_db.values())


def get_bookmark_by_id(bookmark_id: str) -> Dict[str, Any] | None:
    return bookmarks_db.get(bookmark_id)


def delete_bookmark_by_id(bookmark_id: str) -> bool:
    if bookmark_id in bookmarks_db:
        del bookmarks_db[bookmark_id]
        return True
    return False


def filter_bookmarks_by_tag(tag: str) -> List[Dict[str, Any]]:
    result = []
    for b in bookmarks_db.values():
        if tag in b.get("tags", []):
            result.append(b)
    return result
