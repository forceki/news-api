from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.topic import TopicResponse


class NewsCreateRequest(BaseModel):
    title: str
    content: str
    status: int = 1
    published_at: Optional[datetime] = None
    topic_ids: list[int] = []


class NewsUpdateRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[int] = None
    published_at: Optional[datetime] = None
    topic_ids: Optional[list[int]] = None


NEWS_STATUS_MAP = {
    0: "draft",
    1: "published",
    2: "deleted",
}


class NewsResponse(BaseModel):
    id: int
    title: str
    slug: str
    content: str
    status: int
    status_name: str = ""
    published_at: Optional[datetime] = None
    author_id: int
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    topics: list[TopicResponse] = []
