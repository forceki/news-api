import pytest
from httpx import AsyncClient


async def _create_topic(client: AsyncClient, headers: dict, name: str, slug: str) -> int:
    resp = await client.post("/topics", json={"name": name, "slug": slug}, headers=headers)
    return resp.json()["data"]["id"]


class TestCreateNews:
    async def test_create_news_success(self, client: AsyncClient, auth_token):
        response = await client.post("/news", json={
            "title": "Breaking News",
            "slug": "breaking-news",
            "content": "This is breaking news content.",
            "status": 1,
            "topic_ids": [],
        }, headers=auth_token)
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["title"] == "Breaking News"
        assert data["data"]["slug"] == "breaking-news"

    async def test_create_news_with_topics(self, client: AsyncClient, auth_token):
        topic_id = await _create_topic(client, auth_token, "Tech", "tech")

        response = await client.post("/news", json={
            "title": "Tech News",
            "slug": "tech-news",
            "content": "Technology content.",
            "topic_ids": [topic_id],
        }, headers=auth_token)
        assert response.status_code == 201
        data = response.json()["data"]
        assert len(data["topics"]) == 1
        assert data["topics"][0]["name"] == "Tech"

    async def test_create_news_unauthenticated(self, client: AsyncClient):
        response = await client.post("/news", json={
            "title": "Test",
            "slug": "test",
            "content": "Content",
        })
        assert response.status_code == 401

    async def test_create_news_duplicate_slug(self, client: AsyncClient, auth_token):
        await client.post("/news", json={
            "title": "News 1",
            "slug": "same-slug",
            "content": "Content 1",
        }, headers=auth_token)

        response = await client.post("/news", json={
            "title": "News 2",
            "slug": "same-slug",
            "content": "Content 2",
        }, headers=auth_token)
        assert response.status_code == 409
        assert response.json()["error_code"] == "NEWS_SLUG_EXISTS"

    async def test_create_news_invalid_topic_ids(self, client: AsyncClient, auth_token):
        response = await client.post("/news", json={
            "title": "News",
            "slug": "news",
            "content": "Content",
            "topic_ids": [999],
        }, headers=auth_token)
        assert response.status_code == 400
        assert response.json()["error_code"] == "INVALID_TOPIC_IDS"


class TestGetNews:
    async def test_get_all_news(self, client: AsyncClient, auth_token):
        await client.post("/news", json={
            "title": "News 1", "slug": "news-1", "content": "Content 1",
        }, headers=auth_token)
        await client.post("/news", json={
            "title": "News 2", "slug": "news-2", "content": "Content 2",
        }, headers=auth_token)

        response = await client.get("/news", headers=auth_token)
        assert response.status_code == 200
        assert len(response.json()["data"]) == 2

    async def test_get_all_news_unauthenticated(self, client: AsyncClient):
        response = await client.get("/news")
        assert response.status_code == 401

    async def test_get_news_by_id(self, client: AsyncClient, auth_token):
        create_resp = await client.post("/news", json={
            "title": "News", "slug": "news", "content": "Content",
        }, headers=auth_token)
        news_id = create_resp.json()["data"]["id"]

        response = await client.get(f"/news/{news_id}", headers=auth_token)
        assert response.status_code == 200
        assert response.json()["data"]["title"] == "News"

    async def test_get_news_not_found(self, client: AsyncClient, auth_token):
        response = await client.get("/news/999", headers=auth_token)
        assert response.status_code == 404
        assert response.json()["error_code"] == "NEWS_NOT_FOUND"


class TestUpdateNews:
    async def test_update_news_success(self, client: AsyncClient, auth_token):
        create_resp = await client.post("/news", json={
            "title": "Original", "slug": "original", "content": "Content",
        }, headers=auth_token)
        news_id = create_resp.json()["data"]["id"]

        response = await client.put(f"/news/{news_id}", json={
            "title": "Updated Title",
        }, headers=auth_token)
        assert response.status_code == 200
        assert response.json()["data"]["title"] == "Updated Title"

    async def test_update_news_change_topics(self, client: AsyncClient, auth_token):
        topic_id = await _create_topic(client, auth_token, "Sports", "sports")
        create_resp = await client.post("/news", json={
            "title": "News", "slug": "news", "content": "Content",
        }, headers=auth_token)
        news_id = create_resp.json()["data"]["id"]

        response = await client.put(f"/news/{news_id}", json={
            "topic_ids": [topic_id],
        }, headers=auth_token)
        assert response.status_code == 200
        assert len(response.json()["data"]["topics"]) == 1

    async def test_update_news_not_found(self, client: AsyncClient, auth_token):
        response = await client.put("/news/999", json={
            "title": "Updated",
        }, headers=auth_token)
        assert response.status_code == 404


class TestDeleteNews:
    async def test_delete_news_success(self, client: AsyncClient, auth_token):
        create_resp = await client.post("/news", json={
            "title": "News", "slug": "news", "content": "Content",
        }, headers=auth_token)
        news_id = create_resp.json()["data"]["id"]

        response = await client.delete(f"/news/{news_id}", headers=auth_token)
        assert response.status_code == 200

        get_resp = await client.get(f"/news/{news_id}", headers=auth_token)
        assert get_resp.status_code == 404

    async def test_delete_news_not_found(self, client: AsyncClient, auth_token):
        response = await client.delete("/news/999", headers=auth_token)
        assert response.status_code == 404

    async def test_delete_news_unauthenticated(self, client: AsyncClient):
        response = await client.delete("/news/1")
        assert response.status_code == 401
