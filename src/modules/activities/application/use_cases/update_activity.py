from ..dtos.activity_dto import UpdateActivityDTO, ActivityResponseDTO, ActivityDTOMapper
from ...domain.activity_service import ActivityService
from ...domain.activity_events import ActivityUpdatedEvent
from ...domain.interfaces.activity_repository import IActivityRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from shared.events.event_bus import EventBus
from shared.errors.custom_errors import NotFoundError


class UpdateActivityUseCase:
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
        dto: UpdateActivityDTO, 
        user_id: str
    ) -> ActivityResponseDTO:
        """Actualizar actividad existente"""
        activity = await self._activity_repository.find_by_id(activity_id)
        if not activity or not activity.is_active():
            raise NotFoundError("Actividad no encontrada")

        trip_id = await self._activity_service.validate_activity_update(activity, user_id)

        # Determinar qué campos se van a actualizar
        updated_fields = []
        
        if dto.title is not None:
            updated_fields.append("title")
        if dto.description is not None:
            updated_fields.append("description")
        if dto.location is not None:
            updated_fields.append("location")
        if dto.start_time is not None:
            updated_fields.append("start_time")
        if dto.end_time is not None:
            updated_fields.append("end_time")
        if dto.estimated_cost is not None:
            updated_fields.append("estimated_cost")
        if dto.category is not None:
            updated_fields.append("category")

        # Actualizar la actividad
        activity.update_details(
            title=dto.title,
            description=dto.description,
            location=dto.location,
            start_time=dto.start_time,
            end_time=dto.end_time,
            estimated_cost=dto.estimated_cost,
            category=dto.category
        )

        updated_activity = await self._activity_repository.update(activity)

        # Emitir evento si hubo cambios
        if updated_fields:
            event = ActivityUpdatedEvent(
                trip_id=trip_id,
                day_id=activity.day_id,
                activity_id=activity_id,
                updated_by=user_id,
                updated_fields=updated_fields
            )
            await self._event_bus.publish(event)

        # Determinar permisos del usuario
        member = await self._trip_member_repository.find_by_trip_and_user(trip_id, user_id)
        can_edit = member.can_edit_trip() if member else False
        can_change_status = member.is_active() if member else False

        # Obtener información del creador
        creator_user = await self._user_repository.find_by_id(activity.created_by)
        creator_info = creator_user.to_public_dict() if creator_user else None

        return ActivityDTOMapper.to_activity_response(
            updated_activity.to_public_data(),
            can_edit=can_edit,
            can_change_status=can_change_status,
            creator_info=creator_info
        )