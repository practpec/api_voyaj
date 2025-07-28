# src/modules/days/application/use_cases/create_day.py
from ..dtos.day_dto import CreateDayDTO, DayResponseDTO, DayDTOMapper
from ...domain.Day import Day
from ...domain.day_service import DayService
from ...domain.day_events import DayCreatedEvent
from ...domain.interfaces.day_repository import IDayRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from shared.events.event_bus import EventBus


class CreateDayUseCase:
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

    async def execute(self, dto: CreateDayDTO, user_id: str) -> DayResponseDTO:
        """Crear nuevo día en un viaje"""
        await self._day_service.validate_day_creation(
            dto.trip_id,
            dto.date,
            user_id
        )

        day = Day.create(
            trip_id=dto.trip_id,
            date=dto.date,
            notes=dto.notes
        )

        created_day = await self._day_repository.create(day)

        # ✅ Crear evento con argumentos nombrados
        event = DayCreatedEvent(
            trip_id=dto.trip_id,
            day_id=created_day.id,
            date=dto.date,
            created_by=user_id
        )
        await self._event_bus.publish(event)

        member = await self._trip_member_repository.find_by_trip_and_user(dto.trip_id, user_id)
        can_edit = member.can_edit_trip() if member else False

        return DayDTOMapper.to_day_response(
            created_day.to_public_data(),
            can_edit=can_edit,
            activity_count=0,
            photo_count=0
        )