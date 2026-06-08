from typing import Annotated, Optional

from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.model.news import News, news_topics
from app.model.topic import Topic


class NewsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> list[News]:
        result = await self.db.execute(
            select(News).options(selectinload(News.topics)).order_by(News.id.desc())
        )
        return list(result.scalars().all())

    async def get_all_public(
        self,
        status: Optional[int] = None,
        topic_id: Optional[int] = None,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
    ) -> tuple[list[News], int]:
        query = select(News).options(selectinload(News.topics))

        if status is not None:
            query = query.where(News.status == status)
        if topic_id is not None:
            query = query.join(news_topics).where(news_topics.c.topic_id == topic_id)
        if search:
            query = query.where(News.title.ilike(f"%{search}%"))

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginate
        offset = (page - 1) * limit
        query = query.order_by(News.id.desc()).offset(offset).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def get_by_id(self, news_id: int) -> Optional[News]:
        result = await self.db.execute(
            select(News).options(selectinload(News.topics)).where(News.id == news_id)
        )
        return result.scalars().first()

    async def get_by_slug(self, slug: str) -> Optional[News]:
        result = await self.db.execute(
            select(News).options(selectinload(News.topics)).where(News.slug == slug)
        )
        return result.scalars().first()

    async def create(self, news: News) -> News:
        self.db.add(news)
        await self.db.commit()
        await self.db.refresh(news)
        return news

    async def update(self, news: News) -> News:
        await self.db.commit()
        await self.db.refresh(news)
        return news

    async def delete(self, news: News) -> None:
        await self.db.delete(news)
        await self.db.commit()

    async def get_topics_by_ids(self, topic_ids: list[int]) -> list[Topic]:
        result = await self.db.execute(
            select(Topic).where(Topic.id.in_(topic_ids))
        )
        return list(result.scalars().all())


def get_news_repository(db: AsyncSession = Depends(get_db)) -> NewsRepository:
    return NewsRepository(db)


DepNewsRepository = Annotated[NewsRepository, Depends(get_news_repository)]
