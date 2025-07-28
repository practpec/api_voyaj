# src/modules/trips/application/use_cases/update_trip_status.py
from ..dtos.trip_dto import UpdateTripStatusDTO, TripResponseDTO, TripDTOMapper
from ...domain.trip_service import TripService
from ...domain.trip_events import TripStatusChangedEvent, TripCompletedEvent, TripCancelledEvent
from ...domain.interfaces.trip_repository import ITripRepository
from ...domain.interfaces.trip_member_repository import ITripMemberRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from shared.events.event_bus import EventBus
from shared.errors.custom_errors import NotFoundError


class UpdateTripStatusUseCase:
    def __init__(
        self,
        trip_repository: ITripRepository,
        trip_member_repository: ITripMemberRepository,
        user_repository: IUserRepository,
        trip_service: TripService,
        event_bus: EventBus
    ):
        self._trip_repository = trip_repository
        self._trip_member_repository = trip_member_repository
        self._user_repository = user_repository
        self._trip_service = trip_service
        self._event_bus = event_bus

    async def execute(
        self, 
        trip_id: str, 
        dto: UpdateTripStatusDTO, 
        user_id: str
    ) -> TripResponseDTO:
        trip = await self._trip_repository.find_by_id(trip_id)
        if not trip or not trip.is_active():
            raise NotFoundError("Viaje no encontrado")

        await self._trip_service.validate_trip_update(trip, user_id)

        old_status = trip.status
        trip.change_status(dto.status)

        updated_trip = await self._trip_repository.update(trip)

        status_changed_event = TripStatusChangedEvent(
            trip_id=trip_id,
            owner_id=trip.owner_id,
            old_status=old_status,
            new_status=dto.status.value
        )
        await self._event_bus.publish(status_changed_event)

        if dto.status.value == "completed":
            completed_event = TripCompletedEvent(
                trip_id=trip_id,
                owner_id=trip.owner_id
            )
            await self._event_bus.publish(completed_event)
        elif dto.status.value == "cancelled":
            cancelled_event = TripCancelledEvent(
                trip_id=trip_id,
                owner_id=trip.owner_id
            )
            await self._event_bus.publish(cancelled_event)

        user_role = await self._trip_service.get_user_role_in_trip(trip_id, user_id)
        member = await self._trip_member_repository.find_by_trip_and_user(trip_id, user_id)
        can_edit = member.can_edit_trip() if member else False
        owner_user = await self._user_repository.find_by_id(trip.owner_id)

        return TripDTOMapper.to_trip_response(
            updated_trip.to_public_data(),
            owner_user.to_public_dict() if owner_user else None,  # CORREGIDO: Removidos los paréntesis incorrectos
            user_role,
            can_edit
        )