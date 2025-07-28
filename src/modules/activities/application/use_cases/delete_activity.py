from ...domain.activity_service import ActivityService
from ...domain.activity_events import ActivityDeletedEvent
from ...domain.interfaces.activity_repository import IActivityRepository
from shared.events.event_bus import EventBus
from shared.errors.custom_errors import NotFoundError


class DeleteActivityUseCase:
    def __init__(
        self,
        activity_repository: IActivityRepository,
        activity_service: ActivityService,
        event_bus: EventBus
    ):
        self._activity_repository = activity_repository
        self._activity_service = activity_service
        self._event_bus = event_bus

    async def execute(self, activity_id: str, user_id: str) -> bool:
        """Eliminar actividad existente"""
        activity = await self._activity_repository.find_by_id(activity_id)
        # ✅ CORREGIDO: Verificar is_deleted en lugar de is_active()
        if not activity or activity.is_deleted:
            raise NotFoundError("Actividad no encontrada")

        trip_id = await self._activity_service.validate_activity_deletion(activity, user_id)

        # Eliminar actividad (soft delete)
        activity.soft_delete()
        await self._activity_repository.update(activity)

        # Emitir evento
        event = ActivityDeletedEvent(
            trip_id=trip_id,
            day_id=activity.day_id,
            activity_id=activity_id,
            deleted_by=user_id
        )
        await self._event_bus.publish(event)

        return True