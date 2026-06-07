import pytest
from httpx import AsyncClient

from app.core.cache import cache


class TestPublicGetNewsBySlug:
    async def test_get_news_by_slug_success(self, client: AsyncClient, auth_token):
        # Create news via authenticated endpoint
        await client.post("/news", json={
            "title": "Public Article",
            "slug": "public-article",
            "content": "Public content here.",
        }, headers=auth_token)

        # Access via public endpoint (no auth)
        response = await client.get("/public/news/public-article")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["title"] == "Public Article"
        assert data["data"]["slug"] == "public-article"

    async def test_get_news_by_slug_not_found(self, client: AsyncClient):
        response = await client.get("/public/news/nonexistent-slug")
        assert response.status_code == 404
        assert response.json()["error_code"] == "NEWS_NOT_FOUND"

    async def test_get_news_by_slug_cached(self, client: AsyncClient, auth_token):
        await client.post("/news", json={
            "title": "Cached Article",
            "slug": "cached-article",
            "content": "Cached content.",
        }, headers=auth_token)

        # First call — cache miss
        resp1 = await client.get("/public/news/cached-article")
        assert resp1.status_code == 200

        # Verify cache is populated
        cached = cache.get("public:news:slug:cached-article")
        assert cached is not None
        assert cached["title"] == "Cached Article"

        # Second call — cache hit
        resp2 = await client.get("/public/news/cached-article")
        assert resp2.status_code == 200
        assert resp2.json()["data"]["title"] == "Cached Article"

    async def test_get_news_by_slug_no_auth_required(self, client: AsyncClient, auth_token):
        await client.post("/news", json={
            "title": "Open Article",
            "slug": "open-article",
            "content": "Open content.",
        }, headers=auth_token)

        # No Authorization header
        response = await client.get("/public/news/open-article")
        assert response.status_code == 200
