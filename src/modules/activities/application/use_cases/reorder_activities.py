from typing import List
from ..dtos.activity_dto import ReorderActivitiesDTO, ReorderResponseDTO, ActivityListResponseDTO, ActivityDTOMapper
from ...domain.activity_service import ActivityService
from ...domain.activity_events import ActivityOrderChangedEvent
from ...domain.interfaces.activity_repository import IActivityRepository
from shared.events.event_bus import EventBus


class ReorderActivitiesUseCase:
    def __init__(
        self,
        activity_repository: IActivityRepository,
        activity_service: ActivityService,
        event_bus: EventBus
    ):
        self._activity_repository = activity_repository
        self._activity_service = activity_service
        self._event_bus = event_bus

    async def execute(
        self, 
        dto: ReorderActivitiesDTO, 
        user_id: str
    ) -> ReorderResponseDTO:
        """Reordenar actividades de un día"""
        reordered_activities = await self._activity_service.reorder_activities(
            dto.day_id,
            dto.activity_orders,
            user_id
        )

        # Emitir eventos de cambio de orden
        for item in dto.activity_orders:
            activity = next(
                (a for a in reordered_activities if a.id == item["activity_id"]), 
                None
            )
            if activity:
                # Necesitamos obtener el trip_id para el evento
                day = await self._activity_repository._day_repository.find_by_id(dto.day_id)
                trip_id = day.trip_id if day else ""
                
                event = ActivityOrderChangedEvent(
                    trip_id=trip_id,
                    day_id=dto.day_id,
                    activity_id=item["activity_id"],
                    old_order=activity.order,  # Este sería el orden anterior
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