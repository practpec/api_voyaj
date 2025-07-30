# src/modules/activities/application/use_cases/reorder_activities.py
from typing import List
from ..dtos.activity_dto import ReorderActivitiesDTO, ReorderResponseDTO, ActivityListResponseDTO, ActivityDTOMapper
from ...domain.activity_service import ActivityService
from ...domain.activity_events import ActivityOrderChangedEvent
from ...domain.interfaces.activity_repository import IActivityRepository
from modules.days.domain.interfaces.day_repository import IDayRepository
from shared.events.event_bus import EventBus
from shared.errors.custom_errors import NotFoundError


class ReorderActivitiesUseCase:
    def __init__(
        self,
        activity_repository: IActivityRepository,
        day_repository: IDayRepository,
        activity_service: ActivityService,
        event_bus: EventBus
    ):
        self._activity_repository = activity_repository
        self._day_repository = day_repository
        self._activity_service = activity_service
        self._event_bus = event_bus

    async def execute(
        self, 
        day_id: str,
        dto: ReorderActivitiesDTO, 
        user_id: str
    ) -> ReorderResponseDTO:
        """Reordenar actividades de un día"""
        # Usar el day_id del parámetro, no del DTO
        reordered_activities = await self._activity_service.reorder_activities(
            day_id,
            dto.activity_orders,
            user_id
        )

        # Obtener información del día para los eventos
        day = await self._day_repository.find_by_id(day_id)
        if not day:
            raise NotFoundError("Día no encontrado")

        # Emitir eventos de cambio de orden
        for item in dto.activity_orders:
            activity = next(
                (a for a in reordered_activities if a.id == item["activity_id"]), 
                None
            )
            if activity:
                event = ActivityOrderChangedEvent(
                    trip_id=day.trip_id,
                    day_id=day_id,
                    activity_id=item["activity_id"],
                    old_order=activity.order,  # Orden actual después del cambio
                    new_order=item["order"],
                    changed_by=user_id
                )
                await self._event_bus.publish(event)

        # Mapear a DTOs de respuesta
        activity_responses: List[ActivityListResponseDTO] = []
        for activity in reordered_activities:
            activity_response = ActivityDTOMapper.to_activity_list_response(
                activity.to_public_data()
            )
            activity_responses.append(activity_response)

        return ActivityDTOMapper.to_reorder_response(activity_responses)