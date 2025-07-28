# src/modules/trips/application/use_cases/get_trip.py
from ..dtos.trip_dto import TripResponseDTO, TripDTOMapper
from ...domain.trip_service import TripService
from ...domain.interfaces.trip_repository import ITripRepository
from ...domain.interfaces.trip_member_repository import ITripMemberRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from shared.errors.custom_errors import NotFoundError, ForbiddenError


class GetTripUseCase:
    def __init__(
        self,
        trip_repository: ITripRepository,
        trip_member_repository: ITripMemberRepository,
        user_repository: IUserRepository,
        trip_service: TripService
    ):
        self._trip_repository = trip_repository
        self._trip_member_repository = trip_member_repository
        self._user_repository = user_repository
        self._trip_service = trip_service

    async def execute(self, trip_id: str, user_id: str) -> TripResponseDTO:
        trip = await self._trip_repository.find_by_id(trip_id)
        if not trip or not trip.is_active():
            raise NotFoundError("Viaje no encontrado")

        can_access = await self._trip_service.can_user_access_trip(trip, user_id)
        if not can_access:
            raise ForbiddenError("No tienes acceso a este viaje")

        user_role = await self._trip_service.get_user_role_in_trip(trip_id, user_id)
        
        member = await self._trip_member_repository.find_by_trip_and_user(trip_id, user_id)
        can_edit = member.can_edit_trip() if member else False

        owner_user = await self._user_repository.find_by_id(trip.owner_id)

        return TripDTOMapper.to_trip_response(
            trip.to_public_data(),
            owner_user.to_public_dict() if owner_user else None,
            user_role,
            can_edit
        )