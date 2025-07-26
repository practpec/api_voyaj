from ...domain.diary_entry_service import DiaryEntryService
from ...domain.diary_entry_events import DiaryEntryDeletedEvent
from ...domain.interfaces.diary_entry_repository import IDiaryEntryRepository
from shared.events.event_bus import EventBus
from shared.errors.custom_errors import NotFoundError


class DeleteDiaryEntryUseCase:
    def __init__(
        self,
        diary_entry_repository: IDiaryEntryRepository,
        diary_entry_service: DiaryEntryService,
        event_bus: EventBus
    ):
        self._diary_entry_repository = diary_entry_repository
        self._diary_entry_service = diary_entry_service
        self._event_bus = event_bus

    async def execute(self, entry_id: str, user_id: str) -> bool:
        """Eliminar entrada de diario existente"""
        entry = await self._diary_entry_repository.find_by_id(entry_id)
        if not entry or not entry.is_active():
            raise NotFoundError("Entrada de diario no encontrada")

        trip_id = await self._diary_entry_service.validate_entry_deletion(entry, user_id)

        # Eliminar entrada (soft delete)
        entry.soft_delete()
        await self._diary_entry_repository.update(entry)

        # Emitir evento
        event = DiaryEntryDeletedEvent(
            trip_id=trip_id,
            day_id=entry.day_id,
            entry_id=entry_id,
            user_id=entry.user_id,
            deleted_by=user_id
        )
        await self._event_bus.publish(event)

        return True