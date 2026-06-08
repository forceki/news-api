from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TopicCreateRequest(BaseModel):
    name: str


class TopicUpdateRequest(BaseModel):
    name: Optional[str] = None


class TopicResponse(BaseModel):
    id: int
    name: str
    slug: str
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
