from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime

class Bookmark(BaseModel):
    url: HttpUrl
    title: str = Field(min_length=1, max_length=200)
    tags: list[str]
    created_at: datetime