from ..dtos.trip_dto import CreateTripDTO, TripResponseDTO, TripDTOMapper
from ...domain.trip import Trip
from ...domain.trip_member import TripMember
from ...domain.trip_service import TripService
from ...domain.trip_events import TripCreatedEvent, MemberJoinedEvent
from ...domain.interfaces.trip_repository import ITripRepository
from ...domain.interfaces.trip_member_repository import ITripMemberRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from shared.events.event_bus import EventBus


class CreateTripUseCase:
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

    async def execute(self, dto: CreateTripDTO, owner_id: str) -> TripResponseDTO:
        await self._trip_service.validate_trip_creation(
            dto.title,
            dto.start_date,
            dto.end_date,
            owner_id
        )

        trip = Trip.create(
            title=dto.title,
            description=dto.description,
            destination=dto.destination,
            start_date=dto.start_date,
            end_date=dto.end_date,
            owner_id=owner_id,
            category=dto.category,
            is_group_trip=dto.is_group_trip,
            is_public=dto.is_public,
            budget_limit=dto.budget_limit,
            currency=dto.currency,
            image_url=dto.image_url,
            notes=dto.notes
        )

        created_trip = await self._trip_repository.create(trip)

        owner_member = TripMember.create_owner(created_trip.id, owner_id)
        await self._trip_member_repository.create(owner_member)

        trip_created_event = TripCreatedEvent(
            trip_id=created_trip.id,
            owner_id=owner_id,
            title=dto.title,
            destination=dto.destination
        )
        await self._event_bus.publish(trip_created_event)

        member_joined_event = MemberJoinedEvent(
            trip_id=created_trip.id,
            user_id=owner_id,
            role=owner_member.role
        )
        await self._event_bus.publish(member_joined_event)

        owner_user = await self._user_repository.find_by_id(owner_id)
        
        return TripDTOMapper.to_trip_response(
            created_trip.to_public_data(),
            owner_user.to_public_data() if owner_user else None,
            owner_member.role,
            True
        )