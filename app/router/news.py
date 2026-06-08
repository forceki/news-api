from typing import Optional

from app.core.response import success_response
from app.core.security import DepCurrentUser
from app.schemas.news import NewsCreateRequest, NewsResponse, NewsUpdateRequest
from app.schemas.topic import TopicResponse
from app.services.news import DepNewsService
from fastapi import APIRouter, status

router = APIRouter(prefix="/news", tags=["News"])


def _to_response(news) -> dict:
    return NewsResponse(
        id=news.id,
        title=news.title,
        slug=news.slug,
        content=news.content,
        status=news.status,
        published_at=news.published_at,
        author_id=news.author_id,
        created_by=news.created_by,
        created_at=news.created_at,
        updated_at=news.updated_at,
        topics=[
            TopicResponse.model_validate(t, from_attributes=True)
            for t in news.topics
        ],
    ).model_dump(mode="json")


@router.get("")
async def get_all_news(
    news_service: DepNewsService,
    current_user: DepCurrentUser,
    topic_id: Optional[int] = None,
    news_status: Optional[int] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
):
    news_list, total = await news_service.get_all_public(
        status=news_status, topic_id=topic_id, search=search, page=page, limit=limit
    )
    metadata = {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total + limit - 1) // limit if limit > 0 else 0,
    }
    return success_response(
        data=[_to_response(n) for n in news_list],
        message="News retrieved successfully",
        metadata=metadata,
    )


@router.get("/{news_id}")
async def get_news(news_id: int, news_service: DepNewsService, current_user: DepCurrentUser):
    news = await news_service.get_by_id(news_id)
    return success_response(
        data=_to_response(news),
        message="News retrieved successfully",
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_news(
    data: NewsCreateRequest,
    news_service: DepNewsService,
    current_user: DepCurrentUser,
):
    news = await news_service.create(data, user_id=int(current_user["sub"]))
    return success_response(
        data=_to_response(news),
        message="News created successfully",
        status_code=status.HTTP_201_CREATED,
    )


@router.put("/{news_id}")
async def update_news(
    news_id: int,
    data: NewsUpdateRequest,
    news_service: DepNewsService,
    current_user: DepCurrentUser,
):
    news = await news_service.update(news_id, data, user_id=int(current_user["sub"]))
    return success_response(
        data=_to_response(news),
        message="News updated successfully",
    )


@router.delete("/{news_id}")
async def delete_news(
    news_id: int,
    news_service: DepNewsService,
    current_user: DepCurrentUser,
):
    await news_service.delete(news_id)
    return success_response(
        data=None,
        message="News deleted successfully",
    )
