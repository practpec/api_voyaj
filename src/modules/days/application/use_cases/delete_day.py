# src/modules/days/application/use_cases/delete_day.py
from ...domain.day_service import DayService
from ...domain.day_events import DayDeletedEvent
from ...domain.interfaces.day_repository import IDayRepository
from shared.events.event_bus import EventBus
from shared.errors.custom_errors import NotFoundError


class DeleteDayUseCase:
    def __init__(
        self,
        day_repository: IDayRepository,
        day_service: DayService,
        event_bus: EventBus
    ):
        self._day_repository = day_repository
        self._day_service = day_service
        self._event_bus = event_bus

    async def execute(self, day_id: str, user_id: str) -> bool:
        """Eliminar día existente"""
        day = await self._day_repository.find_by_id(day_id)
        if not day or not day.is_active():
            raise NotFoundError("Día no encontrado")

        await self._day_service.validate_day_deletion(day, user_id)

        day.soft_delete()
        await self._day_repository.update(day)

        # ✅ Crear evento con argumentos nombrados
        event = DayDeletedEvent(
            trip_id=day.trip_id,
            day_id=day_id,
            deleted_by=user_id
        )
        await self._event_bus.publish(event)

        return True