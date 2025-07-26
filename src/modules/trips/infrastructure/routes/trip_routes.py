from fastapi import APIRouter, Depends, Query, Path
from typing import Optional
from ..controllers.trip_controller import TripController
from ...application.dtos.trip_dto import (
    CreateTripDTO, UpdateTripDTO, UpdateTripStatusDTO, TripFiltersDTO
)
from ...application.dtos.trip_member_dto import InviteMemberDTO, HandleInvitationDTO
from shared.middleware.AuthMiddleware import get_current_user
from shared.repositories.RepositoryFactory import RepositoryFactory
from shared.services.ServiceFactory import ServiceFactory
from shared.events.event_bus import EventBus

from ...application.use_cases.create_trip import CreateTripUseCase
from ...application.use_cases.get_trip import GetTripUseCase
from ...application.use_cases.get_user_trips import GetUserTripsUseCase
from ...application.use_cases.update_trip import UpdateTripUseCase
from ...application.use_cases.delete_trip import DeleteTripUseCase
from ...application.use_cases.update_trip_status import UpdateTripStatusUseCase
from ...application.use_cases.invite_user_to_trip import InviteUserToTripUseCase
from ...application.use_cases.handle_trip_invitation import HandleTripInvitationUseCase
from ...application.use_cases.get_trip_members import GetTripMembersUseCase
from ...application.use_cases.leave_trip import LeaveTripUseCase
from ...application.use_cases.remove_trip_member import RemoveTripMemberUseCase
from ...application.use_cases.update_member_role import UpdateMemberRoleUseCase

router = APIRouter(prefix="/api/trips", tags=["trips"])

def get_trip_controller():
    trip_repo = RepositoryFactory.get_trip_repository()
    trip_member_repo = RepositoryFactory.get_trip_member_repository()
    user_repo = RepositoryFactory.get_user_repository()
    trip_service = ServiceFactory.get_trip_service()
    event_bus = EventBus.get_instance()
    
    return TripController(
        create_trip_use_case=CreateTripUseCase(
            trip_repo, trip_member_repo, user_repo, trip_service, event_bus
        ),
        get_trip_use_case=GetTripUseCase(
            trip_repo, trip_member_repo, user_repo, trip_service
        ),
        get_user_trips_use_case=GetUserTripsUseCase(
            trip_repo, trip_member_repo, trip_service
        ),
        update_trip_use_case=UpdateTripUseCase(
            trip_repo, trip_member_repo, user_repo, trip_service, event_bus
        ),
        delete_trip_use_case=DeleteTripUseCase(
            trip_repo, trip_member_repo, trip_service, event_bus
        ),
        update_trip_status_use_case=UpdateTripStatusUseCase(
            trip_repo, trip_member_repo, user_repo, trip_service, event_bus
        ),
        invite_user_to_trip_use_case=InviteUserToTripUseCase(
            trip_repo, trip_member_repo, user_repo, trip_service, event_bus
        ),
        handle_trip_invitation_use_case=HandleTripInvitationUseCase(
            trip_repo, trip_member_repo, user_repo, trip_service, event_bus
        ),
        get_trip_members_use_case=GetTripMembersUseCase(
            trip_member_repo, user_repo, trip_service
        ),
        leave_trip_use_case=LeaveTripUseCase(
            trip_repo, trip_member_repo, user_repo, trip_service, event_bus
        ),
        remove_trip_member_use_case=RemoveTripMemberUseCase(
            trip_repo, trip_member_repo, user_repo, trip_service, event_bus
        ),
        update_member_role_use_case=UpdateMemberRoleUseCase(
            trip_repo, trip_member_repo, user_repo, trip_service, event_bus
        )
    )

@router.get("/")
async def get_user_trips(
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    is_group_trip: Optional[bool] = Query(None),
    destination: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    controller: TripController = Depends(get_trip_controller)
):
    return await controller.get_user_trips(current_user, status, category, is_group_trip, destination, limit, offset)

@router.post("/")
async def create_trip(
    dto: CreateTripDTO,
    current_user: dict = Depends(get_current_user),
    controller: TripController = Depends(get_trip_controller)
):
    return await controller.create_trip(dto, current_user)

@router.get("/{trip_id}")
async def get_trip(
    trip_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    controller: TripController = Depends(get_trip_controller)
):
    return await controller.get_trip(trip_id, current_user)

@router.put("/{trip_id}")
async def update_trip(
    trip_id: str = Path(...),
    dto: UpdateTripDTO = None,
    current_user: dict = Depends(get_current_user),
    controller: TripController = Depends(get_trip_controller)
):
    return await controller.update_trip(trip_id, dto, current_user)

@router.delete("/{trip_id}")
async def delete_trip(
    trip_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    controller: TripController = Depends(get_trip_controller)
):
    return await controller.delete_trip(trip_id, current_user)

@router.put("/{trip_id}/status")
async def update_trip_status(
    trip_id: str = Path(...),
    dto: UpdateTripStatusDTO = None,
    current_user: dict = Depends(get_current_user),
    controller: TripController = Depends(get_trip_controller)
):
    return await controller.update_trip_status(trip_id, dto, current_user)

@router.get("/{trip_id}/members")
async def get_trip_members(
    trip_id: str = Path(...),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    controller: TripController = Depends(get_trip_controller)
):
    return await controller.get_trip_members(trip_id, current_user, limit, offset)

@router.post("/{trip_id}/members")
async def invite_member(
    trip_id: str = Path(...),
    dto: InviteMemberDTO = None,
    current_user: dict = Depends(get_current_user),
    controller: TripController = Depends(get_trip_controller)
):
    return await controller.invite_member(trip_id, dto, current_user)

@router.post("/{trip_id}/members/{member_id}/accept")
async def accept_invitation(
    trip_id: str = Path(...),
    member_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    controller: TripController = Depends(get_trip_controller)
):
    return await controller.accept_invitation(trip_id, member_id, current_user)

@router.post("/{trip_id}/members/{member_id}/reject")
async def reject_invitation(
    trip_id: str = Path(...),
    member_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    controller: TripController = Depends(get_trip_controller)
):
    return await controller.reject_invitation(trip_id, member_id, current_user)

@router.post("/{trip_id}/leave")
async def leave_trip(
    trip_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    controller: TripController = Depends(get_trip_controller)
):
    return await controller.leave_trip(trip_id, current_user)