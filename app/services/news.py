from datetime import datetime, timezone
from typing import Annotated, Optional

from fastapi import Depends

from app.core.cache import cache
from app.core.exception import AppError
from app.core.slug import slugify
from app.model.news import News
from app.repository.news import DepNewsRepository, NewsRepository
from app.schemas.news import NewsCreateRequest, NewsUpdateRequest


class NewsService:
    def __init__(self, news_repo: NewsRepository):
        self.news_repo = news_repo

    async def get_all(self) -> list[News]:
        return await self.news_repo.get_all()

    async def get_all_public(
        self,
        status: Optional[int] = None,
        topic_id: Optional[int] = None,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
    ) -> tuple[list[News], int]:
        return await self.news_repo.get_all_public(
            status=status, topic_id=topic_id, search=search, page=page, limit=limit
        )

    async def get_by_id(self, news_id: int) -> News:
        news = await self.news_repo.get_by_id(news_id)
        if not news:
            raise AppError(
                message="News not found",
                status_code=404,
                code="NEWS_NOT_FOUND",
            )
        return news

    async def get_by_slug(self, slug: str) -> News:
        news = await self.news_repo.get_by_slug(slug)
        if not news:
            raise AppError(
                message="News not found",
                status_code=404,
                code="NEWS_NOT_FOUND",
            )
        return news

    async def create(self, data: NewsCreateRequest, user_id: int) -> News:
        slug = slugify(data.title)

        if await self.news_repo.get_by_slug(slug):
            raise AppError(
                message="News slug already exists",
                status_code=409,
                code="NEWS_SLUG_EXISTS",
            )

        topics = []
        if data.topic_ids:
            topics = await self.news_repo.get_topics_by_ids(data.topic_ids)
            if len(topics) != len(data.topic_ids):
                raise AppError(
                    message="One or more topic IDs are invalid",
                    status_code=400,
                    code="INVALID_TOPIC_IDS",
                )

        news = News(
            title=data.title,
            slug=slug,
            content=data.content,
            status=data.status,
            published_at=data.published_at,
            author_id=user_id,
            created_by=user_id,
            topics=topics,
        )
        result = await self.news_repo.create(news)
        cache.invalidate_prefix("public:news:")
        return result

    async def update(self, news_id: int, data: NewsUpdateRequest, user_id: int) -> News:
        news = await self.get_by_id(news_id)

        if data.title is not None and data.title != news.title:
            news.title = data.title
            new_slug = slugify(data.title)
            if new_slug != news.slug:
                if await self.news_repo.get_by_slug(new_slug):
                    raise AppError(
                        message="News slug already exists",
                        status_code=409,
                        code="NEWS_SLUG_EXISTS",
                    )
                news.slug = new_slug
        if data.content is not None:
            news.content = data.content
        if data.status is not None:
            news.status = data.status
        if data.published_at is not None:
            news.published_at = data.published_at

        if data.topic_ids is not None:
            topics = await self.news_repo.get_topics_by_ids(data.topic_ids)
            if len(topics) != len(data.topic_ids):
                raise AppError(
                    message="One or more topic IDs are invalid",
                    status_code=400,
                    code="INVALID_TOPIC_IDS",
                )
            news.topics = topics

        news.updated_at = datetime.now(timezone.utc)
        result = await self.news_repo.update(news)
        cache.invalidate_prefix("public:news:")
        return result

    async def delete(self, news_id: int) -> None:
        news = await self.get_by_id(news_id)
        await self.news_repo.delete(news)
        cache.invalidate_prefix("public:news:")


def get_news_service(news_repo: DepNewsRepository) -> NewsService:
    return NewsService(news_repo)


DepNewsService = Annotated[NewsService, Depends(get_news_service)]
