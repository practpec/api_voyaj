# src/modules/activities/application/use_cases/get_day_activities.py
from ..dtos.activity_dto import DayActivitiesResponseDTO, ActivityDTOMapper, ActivitySummaryDTO
from ...domain.activity_service import ActivityService
from ...domain.interfaces.activity_repository import IActivityRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from modules.days.domain.interfaces.day_repository import IDayRepository
from shared.errors.custom_errors import NotFoundError, ForbiddenError


class GetDayActivitiesUseCase:
    def __init__(
        self,
        activity_repository: IActivityRepository,
        day_repository: IDayRepository,
        trip_member_repository: ITripMemberRepository,
        activity_service: ActivityService
    ):
        self._activity_repository = activity_repository
        self._day_repository = day_repository
        self._trip_member_repository = trip_member_repository
        self._activity_service = activity_service

    async def execute(
        self, 
        day_id: str, 
        user_id: str, 
        include_stats: bool = True
    ) -> DayActivitiesResponseDTO:
        """Obtener actividades de un día"""
        # Verificar que el día existe
        day = await self._day_repository.find_by_id(day_id)
        if not day:
            raise NotFoundError("Día no encontrado")

        # Verificar permisos en el viaje
        trip_member = await self._trip_member_repository.find_by_trip_and_user(
            day.trip_id, user_id
        )
        if not trip_member:
            raise ForbiddenError("No tienes acceso a este día")

        # Obtener actividades ordenadas
        activities = await self._activity_repository.find_by_day_id_ordered(day_id)

        # Generar estadísticas si se solicita
        stats = None
        if include_stats and activities:
            stats = await self._activity_service.generate_day_stats(activities)

        return ActivityDTOMapper.to_day_activities_response(
            day_id=day_id,
            trip_id=day.trip_id,
            activities=[activity.to_public_data() for activity in activities],
            stats=stats
        )