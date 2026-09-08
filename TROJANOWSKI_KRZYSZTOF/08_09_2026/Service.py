from Bookmark import Bookmark

class BookmarkService:
    Bookmarks: list[Bookmark]

    def __init__(self):
        self.Bookmarks = []

    async def AddBookmark(self, NewBookmark: Bookmark) -> bool:
        self.Bookmarks.append(NewBookmark)
        return True

    async def RemoveBookmark(self, id: int) -> bool:
        BookmarkToRemove = await self.GetBookmarkByID(id)

        if(BookmarkToRemove == False):
            return False
        
        self.Bookmarks.remove(BookmarkToRemove)
        return True

    async def GetBookmarkByID(self, id: int) -> Bookmark | bool:
        return self.Bookmarks[id] if id < len(self.Bookmarks) else False

    async def GetBookmarks(self, tag: str) -> list[Bookmark]:
        if(len(tag) == 0):
            return self.Bookmarks

        BookmarkFilter = lambda Bookmark : tag in Bookmark.tags
        return filter(BookmarkFilter, self.Bookmarks)