from typing import Annotated, Optional

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.model.topic import Topic


class TopicRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> list[Topic]:
        result = await self.db.execute(select(Topic).order_by(Topic.id))
        return list(result.scalars().all())

    async def get_by_id(self, topic_id: int) -> Optional[Topic]:
        result = await self.db.execute(
            select(Topic).where(Topic.id == topic_id)
        )
        return result.scalars().first()

    async def get_by_slug(self, slug: str) -> Optional[Topic]:
        result = await self.db.execute(
            select(Topic).where(Topic.slug == slug)
        )
        return result.scalars().first()

    async def get_by_name(self, name: str) -> Optional[Topic]:
        result = await self.db.execute(
            select(Topic).where(Topic.name == name)
        )
        return result.scalars().first()

    async def create(self, topic: Topic) -> Topic:
        self.db.add(topic)
        await self.db.commit()
        await self.db.refresh(topic)
        return topic

    async def update(self, topic: Topic) -> Topic:
        await self.db.commit()
        await self.db.refresh(topic)
        return topic

    async def delete(self, topic: Topic) -> None:
        await self.db.delete(topic)
        await self.db.commit()


def get_topic_repository(db: AsyncSession = Depends(get_db)) -> TopicRepository:
    return TopicRepository(db)


DepTopicRepository = Annotated[TopicRepository, Depends(get_topic_repository)]
