from app.core.response import success_response
from app.core.security import DepCurrentUser
from app.schemas.topic import TopicCreateRequest, TopicResponse, TopicUpdateRequest
from app.services.topic import DepTopicService
from fastapi import APIRouter, status

router = APIRouter(prefix="/topics", tags=["Topics"])


@router.get("")
async def get_all_topics(topic_service: DepTopicService, current_user: DepCurrentUser):
    topics = await topic_service.get_all()
    return success_response(
        data=[TopicResponse.model_validate(t, from_attributes=True).model_dump(mode="json") for t in topics],
        message="Topics retrieved successfully",
    )


@router.get("/{topic_id}")
async def get_topic(topic_id: int, topic_service: DepTopicService, current_user: DepCurrentUser):
    topic = await topic_service.get_by_id(topic_id)
    return success_response(
        data=TopicResponse.model_validate(topic, from_attributes=True).model_dump(mode="json"),
        message="Topic retrieved successfully",
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_topic(
    data: TopicCreateRequest,
    topic_service: DepTopicService,
    current_user: DepCurrentUser,
):
    topic = await topic_service.create(data, user_id=int(current_user["sub"]))
    return success_response(
        data=TopicResponse.model_validate(topic, from_attributes=True).model_dump(mode="json"),
        message="Topic created successfully",
        status_code=status.HTTP_201_CREATED,
    )


@router.put("/{topic_id}")
async def update_topic(
    topic_id: int,
    data: TopicUpdateRequest,
    topic_service: DepTopicService,
    current_user: DepCurrentUser,
):
    topic = await topic_service.update(topic_id, data, user_id=int(current_user["sub"]))
    return success_response(
        data=TopicResponse.model_validate(topic, from_attributes=True).model_dump(mode="json"),
        message="Topic updated successfully",
    )


@router.delete("/{topic_id}", status_code=status.HTTP_200_OK)
async def delete_topic(
    topic_id: int,
    topic_service: DepTopicService,
    current_user: DepCurrentUser,
):
    await topic_service.delete(topic_id)
    return success_response(
        data=None,
        message="Topic deleted successfully",
    )
