from ..dtos.activity_dto import CreateActivityDTO, ActivityResponseDTO, ActivityDTOMapper
from ...domain.activity import Activity
from ...domain.activity_service import ActivityService
from ...domain.activity_events import ActivityCreatedEvent
from ...domain.interfaces.activity_repository import IActivityRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from shared.events.event_bus import EventBus


class CreateActivityUseCase:
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

    async def execute(self, dto: CreateActivityDTO, user_id: str) -> ActivityResponseDTO:
        """Crear nueva actividad en un día"""
        trip_id = await self._activity_service.validate_activity_creation(
            dto.day_id,
            dto.title,
            user_id,
            dto.start_time,
            dto.end_time
        )

    
        # Obtener siguiente orden para el día
        next_order = await self._activity_repository.get_next_order(dto.day_id)
        
        
        activity = Activity.create(
            day_id=dto.day_id,
            title=dto.title,
            created_by=user_id,
            description=dto.description,
            location=dto.location,
            start_time=dto.start_time,
            end_time=dto.end_time,
            estimated_cost=dto.estimated_cost,
            category=dto.category,
            order=next_order
        )
        
        
        created_activity = await self._activity_repository.create(activity)
        

        # Emitir evento
        event = ActivityCreatedEvent(
            trip_id=trip_id,
            day_id=dto.day_id,
            activity_id=created_activity.id,
            title=dto.title,
            created_by=user_id,
            category=dto.category.value
        )
        await self._event_bus.publish(event)

        # Determinar permisos del usuario
        member = await self._trip_member_repository.find_by_trip_and_user(trip_id, user_id)
        can_edit = member.can_edit_trip() if member else False
        can_change_status = member.is_active() if member else False

        # Obtener información del creador
        creator_user = await self._user_repository.find_by_id(user_id)
        creator_info = creator_user.to_public_dict() if creator_user else None

        return ActivityDTOMapper.to_activity_response(
            created_activity.to_public_data(),
            can_edit=can_edit,
            can_change_status=can_change_status,
            creator_info=creator_info
        )