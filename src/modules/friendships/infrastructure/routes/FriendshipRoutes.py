from fastapi import APIRouter, Depends, Query
from typing import Annotated
from ..controllers.friendship_controller import FriendshipController
from ...application.dtos.friendship_dto import SendFriendRequestDTO
from shared.middleware.AuthMiddleware import get_current_user
from shared.repositories.RepositoryFactory import RepositoryFactory
from shared.services.ServiceFactory import ServiceFactory
from shared.events.event_bus import EventBus
from ...application.use_cases.send_friend_request import SendFriendRequestUseCase
from ...application.use_cases.accept_friend_request import AcceptFriendRequestUseCase
from ...application.use_cases.reject_friend_request import RejectFriendRequestUseCase
from ...application.use_cases.remove_friendship import RemoveFriendshipUseCase
from ...application.use_cases.get_friends import GetFriendsUseCase
from ...application.use_cases.get_friend_requests import GetFriendRequestsUseCase
from ...application.use_cases.get_friend_suggestions import GetFriendSuggestionsUseCase
from ...application.use_cases.get_friendship_stats import GetFriendshipStatsUseCase

router = APIRouter()

def get_friendship_controller():
    friendship_repo = RepositoryFactory.get_friendship_repository()
    user_repo = RepositoryFactory.get_user_repository()
    friendship_service = ServiceFactory.get_friendship_service()
    event_bus = EventBus.get_instance()
    
    return FriendshipController(
        send_friend_request_use_case=SendFriendRequestUseCase(friendship_repo, user_repo, friendship_service, event_bus),
        accept_friend_request_use_case=AcceptFriendRequestUseCase(friendship_repo, user_repo, friendship_service, event_bus),
        reject_friend_request_use_case=RejectFriendRequestUseCase(friendship_repo, user_repo, friendship_service, event_bus),
        remove_friendship_use_case=RemoveFriendshipUseCase(friendship_repo, friendship_service, event_bus),
        get_friends_use_case=GetFriendsUseCase(friendship_repo, user_repo, friendship_service),
        get_friend_requests_use_case=GetFriendRequestsUseCase(friendship_repo, user_repo, friendship_service),
        get_friend_suggestions_use_case=GetFriendSuggestionsUseCase(friendship_repo, user_repo, friendship_service),
        get_friendship_stats_use_case=GetFriendshipStatsUseCase(friendship_repo)
    )

@router.post("/request")
async def send_friend_request(
    dto: SendFriendRequestDTO,
    current_user: Annotated[dict, Depends(get_current_user)],
    controller: FriendshipController = Depends(get_friendship_controller)
):
    return await controller.send_friend_request(dto, current_user)

@router.put("/{friendship_id}/accept")
async def accept_friend_request(
    friendship_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    controller: FriendshipController = Depends(get_friendship_controller)
):
    return await controller.accept_friend_request(friendship_id, current_user)

@router.put("/{friendship_id}/reject")
async def reject_friend_request(
    friendship_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    controller: FriendshipController = Depends(get_friendship_controller)
):
    return await controller.reject_friend_request(friendship_id, current_user)

@router.delete("/{friendship_id}")
async def remove_friendship(
    friendship_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    controller: FriendshipController = Depends(get_friendship_controller)
):
    return await controller.remove_friendship(friendship_id, current_user)

@router.get("/")
async def get_friends(
    current_user: Annotated[dict, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    controller: FriendshipController = Depends(get_friendship_controller)
):
    return await controller.get_friends(current_user, page, limit)

@router.get("/requests/received")
async def get_received_requests(
    current_user: Annotated[dict, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    controller: FriendshipController = Depends(get_friendship_controller)
):
    return await controller.get_received_requests(current_user, page, limit)

@router.get("/requests/sent")
async def get_sent_requests(
    current_user: Annotated[dict, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    controller: FriendshipController = Depends(get_friendship_controller)
):
    return await controller.get_sent_requests(current_user, page, limit)

@router.get("/suggestions")
async def get_friend_suggestions(
    current_user: Annotated[dict, Depends(get_current_user)],
    limit: int = Query(10, ge=1, le=50),
    controller: FriendshipController = Depends(get_friendship_controller)
):
    return await controller.get_friend_suggestions(current_user, limit)

@router.get("/stats")
async def get_friendship_stats(
    current_user: Annotated[dict, Depends(get_current_user)],
    controller: FriendshipController = Depends(get_friendship_controller)
):
    return await controller.get_friendship_stats(current_user)