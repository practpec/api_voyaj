from typing import List
from ..dtos.day_dto import GenerateTripDaysDTO, BulkCreateDaysResponseDTO, DayResponseDTO, DayDTOMapper
from ...domain.day_service import DayService
from ...domain.day_events import DayCreatedEvent
from ...domain.interfaces.day_repository import IDayRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from shared.events.event_bus import EventBus


class GenerateTripDaysUseCase:
    def __init__(
        self,
        day_repository: IDayRepository,
        trip_member_repository: ITripMemberRepository,
        day_service: DayService,
        event_bus: EventBus
    ):
        self._day_repository = day_repository
        self._trip_member_repository = trip_member_repository
        self._day_service = day_service
        self._event_bus = event_bus

    async def execute(
        self, 
        dto: GenerateTripDaysDTO, 
        user_id: str
    ) -> BulkCreateDaysResponseDTO:
        """Generar automáticamente todos los días de un viaje"""
        days_to_create = await self._day_service.generate_trip_days(
            dto.trip_id,
            user_id
        )

        if not days_to_create:
            return DayDTOMapper.to_bulk_create_response([], [])

        created_days = await self._day_repository.bulk_create(days_to_create)

        for day in created_days:
            event = DayCreatedEvent(
                trip_id=dto.trip_id,
                day_id=day.id,
                date=day.date,
                created_by=user_id
            )
            await self._event_bus.publish(event)

        member = await self._trip_member_repository.find_by_trip_and_user(dto.trip_id, user_id)
        can_edit = member.can_edit_trip() if member else False

        day_responses: List[DayResponseDTO] = []
        for day in created_days:
            day_response = DayDTOMapper.to_day_response(
                day.to_public_data(),
                can_edit=can_edit,
                activity_count=0,
                photo_count=0
            )
            day_responses.append(day_response)

        return DayDTOMapper.to_bulk_create_response(day_responses, [])