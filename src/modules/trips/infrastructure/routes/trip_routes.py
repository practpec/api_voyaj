from fastapi import APIRouter, Depends
from ..controllers.trip_controller import TripController
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

router = APIRouter()

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

def setup_routes():
    controller = get_trip_controller()
    router.include_router(controller.router)
    return router