from ..dtos.activity_dto import ChangeActivityStatusDTO, ActivityResponseDTO, ActivityDTOMapper
from ...domain.activity import ActivityStatus
from ...domain.activity_service import ActivityService
from ...domain.activity_events import (
    ActivityStartedEvent, ActivityCompletedEvent, ActivityCancelledEvent, ActivityCostUpdatedEvent
)
from ...domain.interfaces.activity_repository import IActivityRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from shared.events.event_bus import EventBus
from shared.errors.custom_errors import NotFoundError


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
        """Cambiar estado de una actividad"""
        activity = await self._activity_repository.find_by_id(activity_id)
        if not activity or not activity.is_active():
            raise NotFoundError("Actividad no encontrada")

        trip_id = await self._activity_service.validate_activity_status_change(
            activity, user_id, dto.status
        )

        old_status = activity.status
        old_cost = activity.actual_cost

        # Cambiar estado según el tipo
        if dto.status == ActivityStatus.IN_PROGRESS:
            activity.start_activity()
            
            # Emitir evento de inicio
            start_event = ActivityStartedEvent(
                trip_id=trip_id,
                day_id=activity.day_id,
                activity_id=activity_id,
                started_by=user_id
            )
            await self._event_bus.publish(start_event)

        elif dto.status == ActivityStatus.COMPLETED:
            activity.complete_activity(dto.actual_cost)
            
            # Emitir evento de completado
            complete_event = ActivityCompletedEvent(
                trip_id=trip_id,
                day_id=activity.day_id,
                activity_id=activity_id,
                completed_by=user_id,
                actual_cost=dto.actual_cost
            )
            await self._event_bus.publish(complete_event)

            # Si se actualizó el costo, emitir evento de costo
            if dto.actual_cost is not None and dto.actual_cost != old_cost:
                cost_event = ActivityCostUpdatedEvent(
                    trip_id=trip_id,
                    day_id=activity.day_id,
                    activity_id=activity_id,
                    old_cost=old_cost,
                    new_cost=dto.actual_cost,
                    updated_by=user_id
                )
                await self._event_bus.publish(cost_event)

        elif dto.status == ActivityStatus.CANCELLED:
            activity.cancel_activity()
            
            # Emitir evento de cancelación
            cancel_event = ActivityCancelledEvent(
                trip_id=trip_id,
                day_id=activity.day_id,
                activity_id=activity_id,
                cancelled_by=user_id
            )
            await self._event_bus.publish(cancel_event)

        else:
            # Cambio de estado genérico
            activity.change_status(dto.status)

        updated_activity = await self._activity_repository.update(activity)

        # Determinar permisos del usuario
        member = await self._trip_member_repository.find_by_trip_and_user(trip_id, user_id)
        can_edit = member.can_edit_trip() if member else False
        can_change_status = member.is_active() if member else False

        # Obtener información del creador
        creator_user = await self._user_repository.find_by_id(activity.created_by)
        creator_info = creator_user.to_public_data() if creator_user else None

        return ActivityDTOMapper.to_activity_response(
            updated_activity.to_public_data(),
            can_edit=can_edit,
            can_change_status=can_change_status,
            creator_info=creator_info
        )