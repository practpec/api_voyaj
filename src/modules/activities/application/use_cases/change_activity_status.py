# src/modules/activities/application/use_cases/change_activity_status.py
from ..dtos.activity_dto import ChangeActivityStatusDTO, ActivityResponseDTO, ActivityDTOMapper
from ...domain.activity_service import ActivityService
from ...domain.activity_events import ActivityStatusChangedEvent, ActivityCompletedEvent
from ...domain.interfaces.activity_repository import IActivityRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from shared.events.event_bus import EventBus
from shared.errors.custom_errors import NotFoundError, ForbiddenError


class ChangeActivityStatusUseCase:
    def __init__(
        self,
        activity_repository: IActivityRepository,
        trip_member_repository: ITripMemberRepository,
        user_repository: IUserRepository,
        activity_service: ActivityService,
        event_bus: EventBus
    ):
        self._activity_repository = activity_repository
        self._trip_member_repository = trip_member_repository
        self._user_repository = user_repository
        self._activity_service = activity_service
        self._event_bus = event_bus

    async def execute(
        self, 
        activity_id: str, 
        dto: ChangeActivityStatusDTO, 
        user_id: str
    ) -> ActivityResponseDTO:
        """Cambiar estado de actividad"""
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

        # Validar cambio de estado
        await self._activity_service.validate_status_change(activity, dto.status, user_id)

        # Guardar estado anterior para eventos
        old_status = activity.status

        # Cambiar estado
        activity.change_status(
            new_status=dto.status,
            notes=dto.notes,
            actual_start_time=dto.actual_start_time,
            actual_end_time=dto.actual_end_time,
            actual_cost=dto.actual_cost
        )

        # Guardar cambios
        updated_activity = await self._activity_repository.update(activity)

        # Publicar eventos
        status_event = ActivityStatusChangedEvent(
            activity_id=activity_id,
            day_id=activity.day_id,
            trip_id=activity.trip_id,
            changed_by=user_id,
            old_status=old_status,
            new_status=dto.status
        )
        await self._event_bus.publish(status_event)

        # Evento específico para completado
        if dto.status == "completed":
            completed_event = ActivityCompletedEvent(
                activity_id=activity_id,
                day_id=activity.day_id,
                trip_id=activity.trip_id,
                completed_by=user_id,
                actual_duration=activity.actual_duration,
                actual_cost=activity.actual_cost
            )
            await self._event_bus.publish(completed_event)

        return ActivityDTOMapper.to_activity_response(updated_activity.to_public_data())