# src/modules/activities/application/use_cases/create_activity.py
from ..dtos.activity_dto import CreateActivityDTO, ActivityResponseDTO, ActivityDTOMapper
from ...domain.activity import Activity
from ...domain.activity_service import ActivityService
from ...domain.activity_events import ActivityCreatedEvent
from ...domain.interfaces.activity_repository import IActivityRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from modules.days.domain.interfaces.day_repository import IDayRepository
from shared.events.event_bus import EventBus
from shared.errors.custom_errors import NotFoundError, ForbiddenError


class CreateActivityUseCase:
    def __init__(
        self,
        activity_repository: IActivityRepository,
        trip_member_repository: ITripMemberRepository,
        user_repository: IUserRepository,
        day_repository: IDayRepository,
        activity_service: ActivityService,
        event_bus: EventBus
    ):
        self._activity_repository = activity_repository
        self._trip_member_repository = trip_member_repository
        self._user_repository = user_repository
        self._day_repository = day_repository
        self._activity_service = activity_service
        self._event_bus = event_bus

    async def execute(self, dto: CreateActivityDTO, user_id: str) -> ActivityResponseDTO:
        """Crear nueva actividad"""
        print(f"[DEBUG] CreateActivity - user_id: {user_id}")
        print(f"[DEBUG] CreateActivity - day_id: {dto.day_id}")
        
        # Verificar que el día existe
        day = await self._day_repository.find_by_id(dto.day_id)
        if not day:
            raise NotFoundError("Día no encontrado")

        print(f"[DEBUG] CreateActivity - day found, trip_id: {day.trip_id}")

        # Verificar permisos en el viaje
        trip_member = await self._trip_member_repository.find_by_trip_and_user(
            day.trip_id, user_id
        )
        
        print(f"[DEBUG] CreateActivity - trip_member found: {trip_member is not None}")
        if trip_member:
            print(f"[DEBUG] CreateActivity - trip_member.role: {trip_member.role}")
            print(f"[DEBUG] CreateActivity - trip_member.status: {trip_member.status}")
            print(f"[DEBUG] CreateActivity - trip_member.is_active(): {trip_member.is_active()}")
            print(f"[DEBUG] CreateActivity - trip_member.can_create_activities(): {trip_member.can_create_activities()}")
        
        if not trip_member or not trip_member.can_create_activities():
            raise ForbiddenError("No tienes permisos para crear actividades en este viaje")

        # Validar datos de la actividad
        await self._activity_service.validate_activity_creation(dto, day)

        # Obtener siguiente orden para la actividad
        next_order = await self._activity_service.get_next_activity_order(dto.day_id)

        # Crear actividad
        activity = Activity.create(
            day_id=dto.day_id,
            trip_id=day.trip_id,
            title=dto.title,
            description=dto.description,
            category=dto.category,
            estimated_duration=dto.estimated_duration,
            estimated_cost=dto.estimated_cost,
            currency=dto.currency,
            location=dto.location,
            coordinates=dto.coordinates,
            notes=dto.notes,
            priority=dto.priority,
            tags=dto.tags or [],
            external_links=dto.external_links or [],
            booking_info=dto.booking_info,
            created_by=user_id,
            order=next_order
        )

        # Guardar en repositorio
        created_activity = await self._activity_repository.create(activity)

        # Publicar evento
        event = ActivityCreatedEvent(
            activity_id=created_activity.id,
            day_id=dto.day_id,
            trip_id=day.trip_id,
            created_by=user_id,
            title=dto.title,
            category=dto.category
        )
        await self._event_bus.publish(event)

        return ActivityDTOMapper.to_activity_response(created_activity.to_public_data())