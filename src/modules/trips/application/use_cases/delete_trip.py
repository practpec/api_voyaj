from ...domain.trip_service import TripService
from ...domain.trip_events import TripDeletedEvent
from ...domain.interfaces.trip_repository import ITripRepository
from ...domain.interfaces.trip_member_repository import ITripMemberRepository
from shared.events.event_bus import EventBus
from shared.errors.custom_errors import NotFoundError


class DeleteTripUseCase:
    def __init__(
        self,
        trip_repository: ITripRepository,
        trip_member_repository: ITripMemberRepository,
        trip_service: TripService,
        event_bus: EventBus
    ):
        self._trip_repository = trip_repository
        self._trip_member_repository = trip_member_repository
        self._trip_service = trip_service
        self._event_bus = event_bus

    async def execute(self, trip_id: str, user_id: str) -> bool:
        trip = await self._trip_repository.find_by_id(trip_id)
        if not trip or not trip.is_active():
            raise NotFoundError("Viaje no encontrado")

        await self._trip_service.validate_trip_deletion(trip, user_id)

        trip.soft_delete()
        await self._trip_repository.update(trip)

        await self._trip_member_repository.delete_by_trip_id(trip_id)

        event = TripDeletedEvent(
            trip_id=trip_id,
            owner_id=trip.owner_id
        )
        await self._event_bus.publish(event)

        return True