import hashlib
from typing import Optional

from app.core.cache import cache
from app.core.response import success_response
from app.schemas.news import NewsResponse
from app.schemas.topic import TopicResponse
from app.services.news import DepNewsService
from fastapi import APIRouter, Request

router = APIRouter(prefix="/public", tags=["Public"])

CACHE_TTL = 3600  # seconds


def _build_cache_key(prefix: str, request: Request) -> str:
    params = dict(sorted(request.query_params.items()))
    raw = f"{request.url.path}:{params}"
    md5_hash = hashlib.md5(raw.encode()).hexdigest()
    return f"{prefix}:{md5_hash}"


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


@router.get("/news")
async def get_all_news(
    request: Request,
    news_service: DepNewsService,
    status: Optional[int] = None,
    topic_id: Optional[int] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
):
    cache_key = _build_cache_key("public:news:list", request)
    cached = cache.get(cache_key)
    if cached is not None:
        return success_response(data=cached["data"], message="News retrieved successfully", metadata=cached["metadata"])

    news_list, total = await news_service.get_all_public(
        status=status, topic_id=topic_id, search=search, page=page, limit=limit
    )
    data = [_to_response(n) for n in news_list]
    metadata = {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total + limit - 1) // limit if limit > 0 else 0,
    }
    cache.set(cache_key, {"data": data, "metadata": metadata}, CACHE_TTL)
    return success_response(data=data, message="News retrieved successfully", metadata=metadata)


@router.get("/news/{slug}")
async def get_news_by_slug(slug: str, request: Request, news_service: DepNewsService):
    cache_key = _build_cache_key("public:news:slug", request)
    cached = cache.get(cache_key)
    if cached is not None:
        return success_response(data=cached, message="News retrieved successfully")

    news = await news_service.get_by_slug(slug)
    data = _to_response(news)
    cache.set(cache_key, data, CACHE_TTL)
    return success_response(data=data, message="News retrieved successfully")
