from ..dtos.day_dto import UpdateDayDTO, DayResponseDTO, DayDTOMapper
from ...domain.day_service import DayService
from ...domain.day_events import DayUpdatedEvent, DayNotesUpdatedEvent
from ...domain.interfaces.day_repository import IDayRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from shared.events.event_bus import EventBus
from shared.errors.custom_errors import NotFoundError


class UpdateDayUseCase:
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
        day_id: str, 
        dto: UpdateDayDTO, 
        user_id: str
    ) -> DayResponseDTO:
        """Actualizar día existente"""
        day = await self._day_repository.find_by_id(day_id)
        if not day or not day.is_active():
            raise NotFoundError("Día no encontrado")

        await self._day_service.validate_day_update(day, user_id)

        updated_fields = []
        old_notes = day.notes

        if dto.notes is not None:
            day.update_notes(dto.notes)
            updated_fields.append("notes")

        updated_day = await self._day_repository.update(day)

        if updated_fields:
            event = DayUpdatedEvent(
                trip_id=day.trip_id,
                day_id=day_id,
                updated_by=user_id,
                updated_fields=updated_fields
            )
            await self._event_bus.publish(event)

            if "notes" in updated_fields and old_notes != dto.notes:
                notes_event = DayNotesUpdatedEvent(
                    trip_id=day.trip_id,
                    day_id=day_id,
                    updated_by=user_id
                )
                await self._event_bus.publish(notes_event)

        member = await self._trip_member_repository.find_by_trip_and_user(day.trip_id, user_id)
        can_edit = member.can_edit_trip() if member else False

        return DayDTOMapper.to_day_response(
            updated_day.to_public_data(),
            can_edit=can_edit,
            activity_count=0,
            photo_count=0
        )