# src/modules/activities/application/use_cases/reorder_activities.py
from ..dtos.activity_dto import ReorderActivitiesDTO, DayActivitiesResponseDTO, ActivityDTOMapper
from ...domain.activity_service import ActivityService
from ...domain.activity_events import ActivitiesReorderedEvent
from ...domain.interfaces.activity_repository import IActivityRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from modules.days.domain.interfaces.day_repository import IDayRepository
from shared.events.event_bus import EventBus
from shared.errors.custom_errors import NotFoundError, ForbiddenError, ValidationError


class ReorderActivitiesUseCase:
    def __init__(
        self,
        activity_repository: IActivityRepository,
        day_repository: IDayRepository,
        trip_member_repository: ITripMemberRepository,
        activity_service: ActivityService,
        event_bus: EventBus
    ):
        self._activity_repository = activity_repository
        self._day_repository = day_repository
        self._trip_member_repository = trip_member_repository
        self._activity_service = activity_service
        self._event_bus = event_bus

    async def execute(
        self, 
        day_id: str, 
        dto: ReorderActivitiesDTO, 
        user_id: str
    ) -> DayActivitiesResponseDTO:
        """Reordenar actividades de un día"""
        # Verificar que el día existe
        day = await self._day_repository.find_by_id(day_id)
        if not day:
            raise NotFoundError("Día no encontrado")

        # Verificar permisos
        trip_member = await self._trip_member_repository.find_by_trip_and_user(
            day.trip_id, user_id
        )
        if not trip_member or not trip_member.can_edit_activities():
            raise ForbiddenError("No tienes permisos para reordenar actividades")

        # Validar datos de reordenamiento
        await self._activity_service.validate_activity_reorder(day_id, dto.activity_orders)

        # Obtener actividades actuales
        current_activities = await self._activity_repository.find_by_day_id(day_id)
        
        # Crear mapeo de ID a actividad
        activity_map = {activity.id: activity for activity in current_activities}

        # Verificar que todas las actividades en la lista existen
        for order_item in dto.activity_orders:
            activity_id = order_item.get("activity_id")
            if activity_id not in activity_map:
                raise ValidationError(f"Actividad {activity_id} no encontrada en este día")

        # Actualizar orden de cada actividad
        updated_activities = []
        for order_item in dto.activity_orders:
            activity_id = order_item.get("activity_id")
            new_order = order_item.get("order")
            
            activity = activity_map[activity_id]
            activity.update_order(new_order)
            
            updated_activity = await self._activity_repository.update(activity)
            updated_activities.append(updated_activity)

        # Publicar evento
        event = ActivitiesReorderedEvent(
            day_id=day_id,
            trip_id=day.trip_id,
            reordered_by=user_id,
            activity_orders=dto.activity_orders
        )
        await self._event_bus.publish(event)

        # Obtener actividades actualizadas ordenadas
        reordered_activities = await self._activity_repository.find_by_day_id_ordered(day_id)

        return ActivityDTOMapper.to_day_activities_response(
            day_id=day_id,
            trip_id=day.trip_id,
            activities=[activity.to_public_data() for activity in reordered_activities]
        )