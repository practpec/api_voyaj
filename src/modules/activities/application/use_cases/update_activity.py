# src/modules/activities/application/use_cases/update_activity.py
from ..dtos.activity_dto import UpdateActivityDTO, ActivityResponseDTO, ActivityDTOMapper
from ...domain.activity_service import ActivityService
from ...domain.activity_events import ActivityUpdatedEvent
from ...domain.interfaces.activity_repository import IActivityRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from shared.events.event_bus import EventBus
from shared.errors.custom_errors import NotFoundError, ForbiddenError


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
        """Actualizar actividad"""
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

        # Validar si puede editar (propietario o admin)
        can_edit = (activity.created_by == user_id or 
                   trip_member.can_edit_activities())
        
        if not can_edit:
            raise ForbiddenError("No tienes permisos para editar esta actividad")

        # Crear diccionario de campos a actualizar
        update_dict = {}
        if dto.title is not None:
            update_dict['title'] = dto.title
        if dto.description is not None:
            update_dict['description'] = dto.description
        if dto.category is not None:
            update_dict['category'] = dto.category
        if dto.estimated_duration is not None:
            update_dict['estimated_duration'] = dto.estimated_duration
        if dto.estimated_cost is not None:
            update_dict['estimated_cost'] = dto.estimated_cost
        if dto.currency is not None:
            update_dict['currency'] = dto.currency
        if dto.location is not None:
            update_dict['location'] = dto.location
        if dto.coordinates is not None:
            update_dict['coordinates'] = dto.coordinates
        if dto.notes is not None:
            update_dict['notes'] = dto.notes
        if dto.priority is not None:
            update_dict['priority'] = dto.priority
        if dto.tags is not None:
            update_dict['tags'] = dto.tags
        if dto.external_links is not None:
            update_dict['external_links'] = dto.external_links
        if dto.booking_info is not None:
            update_dict['booking_info'] = dto.booking_info
        if dto.actual_duration is not None:
            update_dict['actual_duration'] = dto.actual_duration
        if dto.actual_cost is not None:
            update_dict['actual_cost'] = dto.actual_cost
        if dto.rating is not None:
            update_dict['rating'] = dto.rating
        if dto.review is not None:
            update_dict['review'] = dto.review

        # Validar actualización
        await self._activity_service.validate_activity_update(activity, **update_dict)

        # Actualizar actividad
        activity.update_details(**update_dict)

        # Guardar cambios
        updated_activity = await self._activity_repository.update(activity)

        # Publicar evento
        event = ActivityUpdatedEvent(
            activity_id=activity_id,
            day_id=activity.day_id,
            trip_id=activity.trip_id,
            updated_by=user_id,
            updated_fields=list(update_dict.keys())
        )
        await self._event_bus.publish(event)

        return ActivityDTOMapper.to_activity_response(updated_activity.to_public_data())