# src/modules/activity_votes/infrastructure/routes/activity_vote_routes.py
from fastapi import APIRouter, Depends, Path
from ..controllers.activity_vote_controller import ActivityVoteController
from ...application.dtos.activity_vote_dto import CreateActivityVoteDTO, UpdateActivityVoteDTO
from shared.middleware.AuthMiddleware import get_current_user
from shared.repositories.RepositoryFactory import RepositoryFactory
from shared.services.ServiceFactory import ServiceFactory

from ...application.use_cases.create_activity_vote import CreateActivityVoteUseCase
from ...application.use_cases.get_activity_votes import GetActivityVotesUseCase
from ...application.use_cases.update_activity_vote import UpdateActivityVoteUseCase
from ...application.use_cases.delete_activity_vote import DeleteActivityVoteUseCase
from ...application.use_cases.get_trip_rankings import GetTripRankingsUseCase
from ...application.use_cases.get_trip_polls import GetTripPollsUseCase
from ...domain.activity_vote_service import ActivityVoteService

router = APIRouter()

def get_activity_vote_controller():
    activity_vote_repo = RepositoryFactory.get_activity_vote_repository()
    activity_repo = RepositoryFactory.get_activity_repository()
    trip_member_repo = RepositoryFactory.get_trip_member_repository()
    
    activity_vote_service = ActivityVoteService(
        activity_vote_repository=activity_vote_repo,
        activity_repository=activity_repo,
        trip_member_repository=trip_member_repo
    )
    
    create_activity_vote_use_case = CreateActivityVoteUseCase(
        activity_vote_repository=activity_vote_repo,
        activity_vote_service=activity_vote_service
    )
    
    get_activity_votes_use_case = GetActivityVotesUseCase(
        activity_vote_service=activity_vote_service
    )
    
    update_activity_vote_use_case = UpdateActivityVoteUseCase(
        activity_vote_repository=activity_vote_repo,
        activity_vote_service=activity_vote_service
    )
    
    delete_activity_vote_use_case = DeleteActivityVoteUseCase(
        activity_vote_repository=activity_vote_repo,
        activity_vote_service=activity_vote_service
    )
    
    get_trip_rankings_use_case = GetTripRankingsUseCase(
        activity_vote_service=activity_vote_service
    )
    
    get_trip_polls_use_case = GetTripPollsUseCase(
        activity_vote_service=activity_vote_service
    )
    
    return ActivityVoteController(
        create_activity_vote_use_case=create_activity_vote_use_case,
        get_activity_votes_use_case=get_activity_votes_use_case,
        update_activity_vote_use_case=update_activity_vote_use_case,
        delete_activity_vote_use_case=delete_activity_vote_use_case,
        get_trip_rankings_use_case=get_trip_rankings_use_case,
        get_trip_polls_use_case=get_trip_polls_use_case
    )

@router.post("/{activity_id}/vote")
async def vote_activity(
    activity_id: str = Path(...),
    dto: CreateActivityVoteDTO = None,
    current_user: dict = Depends(get_current_user),
    controller: ActivityVoteController = Depends(get_activity_vote_controller)
):
    return await controller.vote_activity(activity_id, dto, current_user)

@router.get("/{activity_id}/votes")
async def get_activity_votes(
    activity_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    controller: ActivityVoteController = Depends(get_activity_vote_controller)
):
    return await controller.get_activity_votes(activity_id, current_user)

@router.put("/{activity_id}/vote")
async def update_activity_vote(
    activity_id: str = Path(...),
    dto: UpdateActivityVoteDTO = None,
    current_user: dict = Depends(get_current_user),
    controller: ActivityVoteController = Depends(get_activity_vote_controller)
):
    return await controller.update_activity_vote(activity_id, dto, current_user)

@router.delete("/{activity_id}/vote")
async def delete_activity_vote(
    activity_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    controller: ActivityVoteController = Depends(get_activity_vote_controller)
):
    return await controller.delete_activity_vote(activity_id, current_user)

@router.get("/trips/{trip_id}/rankings")
async def get_trip_rankings(
    trip_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    controller: ActivityVoteController = Depends(get_activity_vote_controller)
):
    return await controller.get_trip_rankings(trip_id, current_user)

@router.get("/trips/{trip_id}/polls")
async def get_trip_polls(
    trip_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    controller: ActivityVoteController = Depends(get_activity_vote_controller)
):
    return await controller.get_trip_polls(trip_id, current_user)

@router.get("/health")
async def health_check(
    controller: ActivityVoteController = Depends(get_activity_vote_controller)
):
    return await controller.health_check()