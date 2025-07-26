from ...domain.trip_service import TripService
from ...domain.trip_events import MemberLeftEvent
from ...domain.interfaces.trip_repository import ITripRepository
from ...domain.interfaces.trip_member_repository import ITripMemberRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from shared.events.event_bus import EventBus
from shared.errors.custom_errors import NotFoundError


class LeaveTripUseCase:
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

    async def execute(self, trip_id: str, user_id: str) -> bool:
        trip = await self._trip_repository.find_by_id(trip_id)
        if not trip or not trip.is_active():
            raise NotFoundError("Viaje no encontrado")

        member = await self._trip_member_repository.find_by_trip_and_user(trip_id, user_id)
        if not member:
            raise NotFoundError("No eres miembro de este viaje")

        await self._trip_service.validate_member_action(trip, user_id, member, "leave_trip")

        member.leave_trip()
        await self._trip_member_repository.update(member)

        event = MemberLeftEvent(
            trip_id=trip_id,
            user_id=user_id
        )
        await self._event_bus.publish(event)

        return True