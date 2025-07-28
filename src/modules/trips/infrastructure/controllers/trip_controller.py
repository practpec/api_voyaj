# src/modules/trips/infrastructure/controllers/trip_controller.py
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import Annotated, Optional
from datetime import datetime

from ...application.dtos.trip_dto import (
    CreateTripDTO, UpdateTripDTO, UpdateTripStatusDTO, TripFiltersDTO,
    TripResponseDTO, TripListResponseDTO, TripStatsDTO
)
from ...application.dtos.trip_member_dto import (
    InviteMemberDTO, TripMemberResponseDTO, TripMemberListResponseDTO
)
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

from shared.middleware.AuthMiddleware import get_current_user
from shared.utils.response_utils import SuccessResponse, PaginatedResponse
from shared.utils.validation_utils import ValidationUtils
from shared.repositories.RepositoryFactory import RepositoryFactory
from shared.services.ServiceFactory import ServiceFactory
from shared.events.event_bus import EventBus


class TripController:
    def __init__(
        self,
        create_trip_use_case: CreateTripUseCase,
        get_trip_use_case: GetTripUseCase,
        get_user_trips_use_case: GetUserTripsUseCase,
        update_trip_use_case: UpdateTripUseCase,
        delete_trip_use_case: DeleteTripUseCase,
        update_trip_status_use_case: UpdateTripStatusUseCase,
        invite_user_to_trip_use_case: InviteUserToTripUseCase,
        handle_trip_invitation_use_case: HandleTripInvitationUseCase,
        get_trip_members_use_case: GetTripMembersUseCase,
        leave_trip_use_case: LeaveTripUseCase,
        remove_trip_member_use_case: RemoveTripMemberUseCase,
        update_member_role_use_case: UpdateMemberRoleUseCase
    ):
        self.router = APIRouter()
        self._create_trip_use_case = create_trip_use_case
        self._get_trip_use_case = get_trip_use_case
        self._get_user_trips_use_case = get_user_trips_use_case
        self._update_trip_use_case = update_trip_use_case
        self._delete_trip_use_case = delete_trip_use_case
        self._update_trip_status_use_case = update_trip_status_use_case
        self._invite_user_to_trip_use_case = invite_user_to_trip_use_case
        self._handle_trip_invitation_use_case = handle_trip_invitation_use_case
        self._get_trip_members_use_case = get_trip_members_use_case
        self._leave_trip_use_case = leave_trip_use_case
        self._remove_trip_member_use_case = remove_trip_member_use_case
        self._update_member_role_use_case = update_member_role_use_case
        
        self._setup_routes()

    def _setup_routes(self):
        self.router.add_api_route(
            "/",
            self.get_user_trips,
            methods=["GET"],
            response_model=PaginatedResponse[TripListResponseDTO]
        )
        self.router.add_api_route(
            "/",
            self.create_trip,
            methods=["POST"],
            response_model=SuccessResponse[TripResponseDTO]
        )
        self.router.add_api_route(
            "/{trip_id}",
            self.get_trip,
            methods=["GET"],
            response_model=SuccessResponse[TripResponseDTO]
        )
        self.router.add_api_route(
            "/{trip_id}",
            self.update_trip,
            methods=["PUT"],
            response_model=SuccessResponse[TripResponseDTO]
        )
        self.router.add_api_route(
            "/{trip_id}",
            self.delete_trip,
            methods=["DELETE"],
            response_model=SuccessResponse[bool]
        )
        self.router.add_api_route(
            "/{trip_id}/status",
            self.update_trip_status,
            methods=["PUT"],
            response_model=SuccessResponse[TripResponseDTO]
        )
        self.router.add_api_route(
            "/{trip_id}/members",
            self.get_trip_members,
            methods=["GET"],
            response_model=PaginatedResponse[TripMemberListResponseDTO]
        )
        self.router.add_api_route(
            "/{trip_id}/members",
            self.invite_member,
            methods=["POST"],
            response_model=SuccessResponse[TripMemberResponseDTO]
        )
        self.router.add_api_route(
            "/{trip_id}/members/{member_id}/accept",
            self.accept_invitation,
            methods=["POST"],
            response_model=SuccessResponse[TripMemberResponseDTO]
        )
        self.router.add_api_route(
            "/{trip_id}/members/{member_id}/reject",
            self.reject_invitation,
            methods=["POST"],
            response_model=SuccessResponse[bool]
        )
        self.router.add_api_route(
            "/{trip_id}/leave",
            self.leave_trip,
            methods=["POST"],
            response_model=SuccessResponse[bool]
        )

    async def get_user_trips(
        self,
        current_user: Annotated[dict, Depends(get_current_user)],
        status: Optional[str] = Query(None),
        category: Optional[str] = Query(None),
        is_group_trip: Optional[bool] = Query(None),
        destination: Optional[str] = Query(None),
        limit: int = Query(20, ge=1, le=100),
        offset: int = Query(0, ge=0)
    ) -> PaginatedResponse[TripListResponseDTO]:
        filters = TripFiltersDTO(
            status=status,
            category=category,
            is_group_trip=is_group_trip,
            destination=destination,
            limit=limit,
            offset=offset
        )
        
        result = await self._get_user_trips_use_case.execute(
            current_user["sub"],
            filters
        )
        return result

    async def create_trip(
        self,
        dto: CreateTripDTO,
        current_user: Annotated[dict, Depends(get_current_user)]
    ) -> SuccessResponse[TripResponseDTO]:
        # FastAPI y Pydantic ya validan los campos requeridos del DTO
        result = await self._create_trip_use_case.execute(dto, current_user["sub"])
        
        return SuccessResponse(
            data=result,
            message="Viaje creado exitosamente"
        )

    async def get_trip(
        self,
        trip_id: Annotated[str, Path()],
        current_user: Annotated[dict, Depends(get_current_user)]
    ) -> SuccessResponse[TripResponseDTO]:
        result = await self._get_trip_use_case.execute(trip_id, current_user["sub"])
        
        return SuccessResponse(data=result)

    async def update_trip(
        self,
        trip_id: Annotated[str, Path()],
        dto: UpdateTripDTO,
        current_user: Annotated[dict, Depends(get_current_user)]
    ) -> SuccessResponse[TripResponseDTO]:
        result = await self._update_trip_use_case.execute(trip_id, dto, current_user["sub"])
        
        return SuccessResponse(
            data=result,
            message="Viaje actualizado exitosamente"
        )

    async def delete_trip(
        self,
        trip_id: Annotated[str, Path()],
        current_user: Annotated[dict, Depends(get_current_user)]
    ) -> SuccessResponse[bool]:
        result = await self._delete_trip_use_case.execute(trip_id, current_user["sub"])
        
        return SuccessResponse(
            data=result,
            message="Viaje eliminado exitosamente"
        )

    async def invite_member(
        self,
        trip_id: Annotated[str, Path()],
        dto: InviteMemberDTO,
        current_user: Annotated[dict, Depends(get_current_user)]
    ) -> SuccessResponse[TripMemberResponseDTO]:
        # FastAPI y Pydantic ya validan los campos requeridos del DTO
        result = await self._invite_user_to_trip_use_case.execute(
            trip_id, dto, current_user["sub"]
        )
        
        return SuccessResponse(
            data=result,
            message="Invitación enviada exitosamente"
        )
    
    async def update_trip_status(
        self,
        trip_id: Annotated[str, Path()],
        dto: UpdateTripStatusDTO,
        current_user: Annotated[dict, Depends(get_current_user)]
    ) -> SuccessResponse[TripResponseDTO]:
        result = await self._update_trip_status_use_case.execute(
            trip_id, dto, current_user["sub"]
        )
        
        return SuccessResponse(
            data=result,
            message="Estado del viaje actualizado exitosamente"
        )

    async def get_trip_members(
        self,
        trip_id: Annotated[str, Path()],
        current_user: Annotated[dict, Depends(get_current_user)],
        limit: int = Query(50, ge=1, le=100),
        offset: int = Query(0, ge=0)
    ) -> PaginatedResponse[TripMemberListResponseDTO]:
        from ...application.dtos.trip_member_dto import TripMemberFiltersDTO
        
        filters = TripMemberFiltersDTO(
            limit=limit,
            offset=offset
        )
        
        result = await self._get_trip_members_use_case.execute(
            trip_id, current_user["sub"], filters
        )
        return result

    async def accept_invitation(
        self,
        trip_id: Annotated[str, Path()],
        member_id: Annotated[str, Path()],
        current_user: Annotated[dict, Depends(get_current_user)]
    ) -> SuccessResponse[TripMemberResponseDTO]:
        from ...application.dtos.trip_member_dto import HandleInvitationDTO
        
        dto = HandleInvitationDTO(action="accept")
        
        result = await self._handle_trip_invitation_use_case.execute(
            trip_id, member_id, dto, current_user["sub"]
        )
        
        return SuccessResponse(
            data=result,
            message="Invitación aceptada exitosamente"
        )

    async def reject_invitation(
        self,
        trip_id: Annotated[str, Path()],
        member_id: Annotated[str, Path()],
        current_user: Annotated[dict, Depends(get_current_user)]
    ) -> SuccessResponse[bool]:
        from ...application.dtos.trip_member_dto import HandleInvitationDTO
        
        dto = HandleInvitationDTO(action="reject")
        
        await self._handle_trip_invitation_use_case.execute(
            trip_id, member_id, dto, current_user["sub"]
        )
        
        return SuccessResponse(
            data=True,
            message="Invitación rechazada exitosamente"
        )

    async def leave_trip(
        self,
        trip_id: Annotated[str, Path()],
        current_user: Annotated[dict, Depends(get_current_user)]
    ) -> SuccessResponse[bool]:
        result = await self._leave_trip_use_case.execute(trip_id, current_user["sub"])
        
        return SuccessResponse(
            data=result,
            message="Has abandonado el viaje exitosamente"
        )