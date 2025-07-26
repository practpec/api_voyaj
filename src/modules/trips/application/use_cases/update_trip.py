from ..dtos.trip_dto import UpdateTripDTO, TripResponseDTO, TripDTOMapper
from ...domain.trip_service import TripService
from ...domain.trip_events import TripUpdatedEvent
from ...domain.interfaces.trip_repository import ITripRepository
from ...domain.interfaces.trip_member_repository import ITripMemberRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from shared.events.event_bus import EventBus
from shared.errors.custom_errors import NotFoundError


class UpdateTripUseCase:
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
        dto: UpdateTripDTO, 
        user_id: str
    ) -> TripResponseDTO:
        trip = await self._trip_repository.find_by_id(trip_id)
        if not trip or not trip.is_active():
            raise NotFoundError("Viaje no encontrado")

        update_dict = {}
        if dto.title is not None:
            update_dict['title'] = dto.title
        if dto.description is not None:
            update_dict['description'] = dto.description
        if dto.destination is not None:
            update_dict['destination'] = dto.destination
        if dto.start_date is not None:
            update_dict['start_date'] = dto.start_date
        if dto.end_date is not None:
            update_dict['end_date'] = dto.end_date
        if dto.category is not None:
            update_dict['category'] = dto.category
        if dto.budget_limit is not None:
            update_dict['budget_limit'] = dto.budget_limit
        if dto.is_public is not None:
            update_dict['is_public'] = dto.is_public
        if dto.image_url is not None:
            update_dict['image_url'] = dto.image_url
        if dto.notes is not None:
            update_dict['notes'] = dto.notes

        await self._trip_service.validate_trip_update(trip, user_id, **update_dict)

        trip.update_details(
            title=dto.title,
            description=dto.description,
            destination=dto.destination,
            start_date=dto.start_date,
            end_date=dto.end_date,
            category=dto.category,
            budget_limit=dto.budget_limit,
            is_public=dto.is_public,
            image_url=dto.image_url,
            notes=dto.notes
        )

        updated_trip = await self._trip_repository.update(trip)

        event = TripUpdatedEvent(
            trip_id=trip_id,
            owner_id=trip.owner_id,
            updated_fields=list(update_dict.keys())
        )
        await self._event_bus.publish(event)

        user_role = await self._trip_service.get_user_role_in_trip(trip_id, user_id)
        member = await self._trip_member_repository.find_by_trip_and_user(trip_id, user_id)
        can_edit = member.can_edit_trip() if member else False
        owner_user = await self._user_repository.find_by_id(trip.owner_id)

        return TripDTOMapper.to_trip_response(
            updated_trip.to_public_data(),
            owner_user.to_public_data() if owner_user else None,
            user_role,
            can_edit
        )