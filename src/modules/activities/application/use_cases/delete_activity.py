# src/modules/activities/application/use_cases/delete_activity.py
from ...domain.activity_service import ActivityService
from ...domain.activity_events import ActivityDeletedEvent
from ...domain.interfaces.activity_repository import IActivityRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from shared.events.event_bus import EventBus
from shared.errors.custom_errors import NotFoundError, ForbiddenError


class DeleteActivityUseCase:
    def __init__(
        self,
        activity_repository: IActivityRepository,
        trip_member_repository: ITripMemberRepository,
        activity_service: ActivityService,
        event_bus: EventBus
    ):
        self._activity_repository = activity_repository
        self._trip_member_repository = trip_member_repository
        self._activity_service = activity_service
        self._event_bus = event_bus

    async def execute(self, activity_id: str, user_id: str) -> bool:
        """Eliminar actividad (soft delete)"""
        # Buscar actividad
        activity = await self._activity_repository.find_by_id(activity_id)
        if not activity or not activity.is_active():
            raise NotFoundError("Actividad no encontrada")

        # Verificar permisos
        trip_member = await self._trip_member_repository.find_by_trip_and_user(
            activity.trip_id, user_id
        )
        if not trip_member:
            raise ForbiddenError("No tienes acceso a esta actividad")

        # Validar si puede eliminar (propietario o admin)
        can_delete = (activity.created_by == user_id or 
                     trip_member.can_delete_activities())
        
        if not can_delete:
            raise ForbiddenError("No tienes permisos para eliminar esta actividad")

        # Validar eliminación
        await self._activity_service.validate_activity_deletion(activity, user_id)

        # Eliminar actividad (soft delete)
        success = await self._activity_repository.delete(activity_id)

        if success:
            # Publicar evento
            event = ActivityDeletedEvent(
                activity_id=activity_id,
                day_id=activity.day_id,
                trip_id=activity.trip_id,
                deleted_by=user_id,
                title=activity.title
            )
            await self._event_bus.publish(event)

        return success