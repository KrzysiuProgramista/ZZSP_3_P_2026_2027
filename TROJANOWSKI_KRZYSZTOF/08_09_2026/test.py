import unittest
from datetime import datetime, timezone

from Bookmark import Bookmark
from Service import BookmarkService


class TestBookmarkService(unittest.IsolatedAsyncioTestCase):
    def create_bookmark(
        self,
        url: str = "https://example.com",
        title: str = "Example",
        tags: list[str] | None = None,
    ) -> Bookmark:
        return Bookmark(
            url=url,
            title=title,
            tags=tags or [],
            created_at=datetime.now(timezone.utc),
        )

    async def test_service_starts_with_empty_bookmarks(self):
        service = BookmarkService()

        self.assertEqual(service.Bookmarks, [])

    async def test_add_bookmark_returns_true(self):
        service = BookmarkService()
        bookmark = self.create_bookmark()

        result = await service.AddBookmark(bookmark)

        self.assertTrue(result)

    async def test_add_bookmark_stores_bookmark(self):
        service = BookmarkService()
        bookmark = self.create_bookmark()

        await service.AddBookmark(bookmark)

        self.assertEqual(len(service.Bookmarks), 1)
        self.assertIs(service.Bookmarks[0], bookmark)

    async def test_get_bookmark_by_id_returns_bookmark(self):
        service = BookmarkService()
        bookmark = self.create_bookmark()
        await service.AddBookmark(bookmark)

        result = await service.GetBookmarkByID(0)

        self.assertIs(result, bookmark)

    async def test_get_bookmark_by_invalid_id_returns_false(self):
        service = BookmarkService()

        result = await service.GetBookmarkByID(0)

        self.assertFalse(result)

    async def test_remove_bookmark_returns_true_and_removes_bookmark(self):
        service = BookmarkService()
        bookmark = self.create_bookmark()
        await service.AddBookmark(bookmark)

        result = await service.RemoveBookmark(0)

        self.assertTrue(result)
        self.assertEqual(service.Bookmarks, [])

    async def test_remove_bookmark_with_invalid_id_returns_false(self):
        service = BookmarkService()

        result = await service.RemoveBookmark(0)

        self.assertFalse(result)

    async def test_get_bookmarks_filters_by_tag(self):
        service = BookmarkService()

        python_bookmark = self.create_bookmark(
            url="https://python.org",
            title="Python",
            tags=["python", "programming"],
        )
        cooking_bookmark = self.create_bookmark(
            url="https://example.com/cooking",
            title="Cooking",
            tags=["cooking"],
        )

        await service.AddBookmark(python_bookmark)
        await service.AddBookmark(cooking_bookmark)

        result = await service.GetBookmarks("python")

        self.assertEqual(list(result), [python_bookmark])


if __name__ == "__main__":
    unittest.main()