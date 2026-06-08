import pytest
from httpx import AsyncClient

from app.core.cache import cache


class TestPublicGetAllNews:
    async def test_get_all_news_public(self, client: AsyncClient, auth_token):
        await client.post("/news", json={
            "title": "News One", "content": "Content 1",
        }, headers=auth_token)
        await client.post("/news", json={
            "title": "News Two", "content": "Content 2",
        }, headers=auth_token)

        response = await client.get("/public/news")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        assert data["metadata"]["total"] == 2
        assert data["metadata"]["page"] == 1

    async def test_get_all_news_pagination(self, client: AsyncClient, auth_token):
        for i in range(5):
            await client.post("/news", json={
                "title": f"News Item {i}", "content": f"Content {i}",
            }, headers=auth_token)

        response = await client.get("/public/news?page=1&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        assert data["metadata"]["total"] == 5
        assert data["metadata"]["total_pages"] == 3

        response2 = await client.get("/public/news?page=2&limit=2")
        assert response2.status_code == 200
        assert len(response2.json()["data"]) == 2

    async def test_get_all_news_filter_by_status(self, client: AsyncClient, auth_token):
        await client.post("/news", json={
            "title": "Active News", "content": "Content", "status": 1,
        }, headers=auth_token)
        await client.post("/news", json={
            "title": "Draft News", "content": "Content", "status": 0,
        }, headers=auth_token)

        response = await client.get("/public/news?status=1")
        assert response.status_code == 200
        assert len(response.json()["data"]) == 1
        assert response.json()["data"][0]["title"] == "Active News"

    async def test_get_all_news_search(self, client: AsyncClient, auth_token):
        await client.post("/news", json={
            "title": "Python Tutorial", "content": "Content",
        }, headers=auth_token)
        await client.post("/news", json={
            "title": "Java Guide", "content": "Content",
        }, headers=auth_token)

        response = await client.get("/public/news?search=Python")
        assert response.status_code == 200
        assert len(response.json()["data"]) == 1
        assert response.json()["data"][0]["title"] == "Python Tutorial"

    async def test_get_all_news_cached_with_md5(self, client: AsyncClient, auth_token):
        await client.post("/news", json={
            "title": "Cached News", "content": "Content",
        }, headers=auth_token)

        resp1 = await client.get("/public/news?page=1&limit=10")
        assert resp1.status_code == 200

        resp2 = await client.get("/public/news?page=2&limit=10")
        assert resp2.status_code == 200

        resp3 = await client.get("/public/news?page=1&limit=10")
        assert resp3.status_code == 200
        assert resp3.json()["data"] == resp1.json()["data"]

    async def test_get_all_news_no_auth_required(self, client: AsyncClient):
        response = await client.get("/public/news")
        assert response.status_code == 200
        assert response.json()["data"] == []


class TestPublicGetNewsBySlug:
    async def test_get_news_by_slug_success(self, client: AsyncClient, auth_token):
        await client.post("/news", json={
            "title": "Public Article",
            "content": "Public content here.",
        }, headers=auth_token)

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
            "content": "Cached content.",
        }, headers=auth_token)

        resp1 = await client.get("/public/news/cached-article")
        assert resp1.status_code == 200

        resp2 = await client.get("/public/news/cached-article")
        assert resp2.status_code == 200
        assert resp2.json()["data"]["title"] == "Cached Article"

    async def test_get_news_by_slug_no_auth_required(self, client: AsyncClient, auth_token):
        await client.post("/news", json={
            "title": "Open Article",
            "content": "Open content.",
        }, headers=auth_token)

        response = await client.get("/public/news/open-article")
        assert response.status_code == 200
