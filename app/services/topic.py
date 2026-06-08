from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends

from app.core.exception import AppError
from app.core.slug import slugify
from app.model.topic import Topic
from app.repository.topic import DepTopicRepository, TopicRepository
from app.schemas.topic import TopicCreateRequest, TopicUpdateRequest


class TopicService:
    def __init__(self, topic_repo: TopicRepository):
        self.topic_repo = topic_repo

    async def get_all(self) -> list[Topic]:
        return await self.topic_repo.get_all()

    async def get_by_id(self, topic_id: int) -> Topic:
        topic = await self.topic_repo.get_by_id(topic_id)
        if not topic:
            raise AppError(
                message="Topic not found",
                status_code=404,
                code="TOPIC_NOT_FOUND",
            )
        return topic

    async def create(self, data: TopicCreateRequest, user_id: int) -> Topic:
        slug = slugify(data.name)

        if await self.topic_repo.get_by_name(data.name):
            raise AppError(
                message="Topic name already exists",
                status_code=409,
                code="TOPIC_NAME_EXISTS",
            )
        if await self.topic_repo.get_by_slug(slug):
            raise AppError(
                message="Topic slug already exists",
                status_code=409,
                code="TOPIC_SLUG_EXISTS",
            )

        topic = Topic(
            name=data.name,
            slug=slug,
            created_by=user_id,
        )
        return await self.topic_repo.create(topic)

    async def update(self, topic_id: int, data: TopicUpdateRequest, user_id: int) -> Topic:
        topic = await self.get_by_id(topic_id)

        if data.name and data.name != topic.name:
            existing = await self.topic_repo.get_by_name(data.name)
            if existing:
                raise AppError(
                    message="Topic name already exists",
                    status_code=409,
                    code="TOPIC_NAME_EXISTS",
                )
            topic.name = data.name
            new_slug = slugify(data.name)
            if new_slug != topic.slug:
                if await self.topic_repo.get_by_slug(new_slug):
                    raise AppError(
                        message="Topic slug already exists",
                        status_code=409,
                        code="TOPIC_SLUG_EXISTS",
                    )
                topic.slug = new_slug

        topic.updated_by = user_id
        topic.updated_at = datetime.now(timezone.utc)
        return await self.topic_repo.update(topic)

    async def delete(self, topic_id: int) -> None:
        topic = await self.get_by_id(topic_id)
        await self.topic_repo.delete(topic)


def get_topic_service(topic_repo: DepTopicRepository) -> TopicService:
    return TopicService(topic_repo)


DepTopicService = Annotated[TopicService, Depends(get_topic_service)]
