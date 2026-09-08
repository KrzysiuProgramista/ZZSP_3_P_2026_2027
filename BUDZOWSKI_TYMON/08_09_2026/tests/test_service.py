"""The service is plain Python, so it is testable without any HTTP."""

import uuid

import pytest

from app.models import BookmarkCreate
from app.service import BookmarkNotFound, BookmarkService


def bookmark(title="Example", tags=None):
    return BookmarkCreate(
        url="https://example.com", title=title, tags=tags if tags is not None else []
    )


def test_add_assigns_unique_ids():
    service = BookmarkService()
    first = service.add(bookmark("One"))
    second = service.add(bookmark("Two"))
    assert first.id != second.id


def test_get_and_delete_raise_for_unknown_ids():
    service = BookmarkService()
    missing = uuid.uuid4()
    with pytest.raises(BookmarkNotFound):
        service.get(missing)
    with pytest.raises(BookmarkNotFound):
        service.delete(missing)


def test_list_by_tag_matches_normalized_tags():
    service = BookmarkService()
    service.add(bookmark("Tagged", tags=["Read Later"]))
    service.add(bookmark("Untagged"))
    assert [b.title for b in service.list(tag="read later")] == ["Tagged"]
    assert len(service.list()) == 2
