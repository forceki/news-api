from app.core.cache import cache
from app.core.response import success_response
from app.schemas.news import NewsResponse
from app.schemas.topic import TopicResponse
from app.services.news import DepNewsService
from fastapi import APIRouter

router = APIRouter(prefix="/public", tags=["Public"])

CACHE_TTL = 3600  # seconds


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


@router.get("/news/{slug}")
async def get_news_by_slug(slug: str, news_service: DepNewsService):
    cache_key = f"public:news:slug:{slug}"
    cached = cache.get(cache_key)
    if cached is not None:
        return success_response(data=cached, message="News retrieved successfully")

    news = await news_service.get_by_slug(slug)
    data = _to_response(news)
    cache.set(cache_key, data, CACHE_TTL)
    return success_response(data=data, message="News retrieved successfully")
