import pytest
from httpx import AsyncClient


class TestCreateTopic:
    async def test_create_topic_success(self, client: AsyncClient, auth_token):
        response = await client.post("/topics", json={
            "name": "Technology",
            "slug": "technology",
        }, headers=auth_token)
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Technology"
        assert data["data"]["slug"] == "technology"

    async def test_create_topic_unauthenticated(self, client: AsyncClient):
        response = await client.post("/topics", json={
            "name": "Technology",
            "slug": "technology",
        })
        assert response.status_code == 401

    async def test_create_topic_duplicate_name(self, client: AsyncClient, auth_token):
        await client.post("/topics", json={
            "name": "Technology",
            "slug": "technology",
        }, headers=auth_token)

        response = await client.post("/topics", json={
            "name": "Technology",
            "slug": "tech-2",
        }, headers=auth_token)
        assert response.status_code == 409
        assert response.json()["error_code"] == "TOPIC_NAME_EXISTS"

    async def test_create_topic_duplicate_slug(self, client: AsyncClient, auth_token):
        await client.post("/topics", json={
            "name": "Technology",
            "slug": "technology",
        }, headers=auth_token)

        response = await client.post("/topics", json={
            "name": "Tech News",
            "slug": "technology",
        }, headers=auth_token)
        assert response.status_code == 409
        assert response.json()["error_code"] == "TOPIC_SLUG_EXISTS"


class TestGetTopics:
    async def test_get_all_topics(self, client: AsyncClient, auth_token):
        await client.post("/topics", json={"name": "Tech", "slug": "tech"}, headers=auth_token)
        await client.post("/topics", json={"name": "Sports", "slug": "sports"}, headers=auth_token)

        response = await client.get("/topics", headers=auth_token)
        assert response.status_code == 200
        assert len(response.json()["data"]) == 2

    async def test_get_all_topics_unauthenticated(self, client: AsyncClient):
        response = await client.get("/topics")
        assert response.status_code == 401

    async def test_get_topic_by_id(self, client: AsyncClient, auth_token):
        create_resp = await client.post("/topics", json={
            "name": "Tech", "slug": "tech",
        }, headers=auth_token)
        topic_id = create_resp.json()["data"]["id"]

        response = await client.get(f"/topics/{topic_id}", headers=auth_token)
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "Tech"

    async def test_get_topic_not_found(self, client: AsyncClient, auth_token):
        response = await client.get("/topics/999", headers=auth_token)
        assert response.status_code == 404
        assert response.json()["error_code"] == "TOPIC_NOT_FOUND"


class TestUpdateTopic:
    async def test_update_topic_success(self, client: AsyncClient, auth_token):
        create_resp = await client.post("/topics", json={
            "name": "Tech", "slug": "tech",
        }, headers=auth_token)
        topic_id = create_resp.json()["data"]["id"]

        response = await client.put(f"/topics/{topic_id}", json={
            "name": "Technology Updated",
        }, headers=auth_token)
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "Technology Updated"

    async def test_update_topic_not_found(self, client: AsyncClient, auth_token):
        response = await client.put("/topics/999", json={
            "name": "Updated",
        }, headers=auth_token)
        assert response.status_code == 404


class TestDeleteTopic:
    async def test_delete_topic_success(self, client: AsyncClient, auth_token):
        create_resp = await client.post("/topics", json={
            "name": "Tech", "slug": "tech",
        }, headers=auth_token)
        topic_id = create_resp.json()["data"]["id"]

        response = await client.delete(f"/topics/{topic_id}", headers=auth_token)
        assert response.status_code == 200

        get_resp = await client.get(f"/topics/{topic_id}", headers=auth_token)
        assert get_resp.status_code == 404

    async def test_delete_topic_not_found(self, client: AsyncClient, auth_token):
        response = await client.delete("/topics/999", headers=auth_token)
        assert response.status_code == 404
