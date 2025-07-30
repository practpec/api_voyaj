# src/modules/activities/application/use_cases/get_day_activities.py
from typing import List
from ..dtos.activity_dto import DayActivitiesResponseDTO, ActivityListResponseDTO, ActivityDTOMapper
from ...domain.activity_service import ActivityService
from ...domain.interfaces.activity_repository import IActivityRepository
from modules.days.domain.interfaces.day_repository import IDayRepository
from shared.errors.custom_errors import NotFoundError, ForbiddenError


class GetDayActivitiesUseCase:
    def __init__(
        self,
        activity_repository: IActivityRepository,
        day_repository: IDayRepository,
        activity_service: ActivityService
    ):
        self._activity_repository = activity_repository
        self._day_repository = day_repository
        self._activity_service = activity_service

    async def execute(
        self, 
        day_id: str, 
        user_id: str, 
        include_stats: bool = True
    ) -> DayActivitiesResponseDTO:
        """Obtener todas las actividades de un día específico"""
        day = await self._day_repository.find_by_id(day_id)
        if not day or not day.is_active():
            raise NotFoundError("Día no encontrado")

        # Verificar acceso del usuario al viaje
        try:
            await self._activity_service._validate_user_permissions(day.trip_id, user_id, "view_activities")
        except Exception:
            raise ForbiddenError("No tienes acceso a las actividades de este viaje")

        # Obtener actividades del día ordenadas
        activities = await self._activity_repository.find_by_day_id_ordered(day_id)

        # Mapear actividades a DTOs
        activity_list_responses: List[ActivityListResponseDTO] = []
        for activity in activities:
            activity_response = ActivityDTOMapper.to_activity_list_response(
                activity.to_public_data()
            )
            activity_list_responses.append(activity_response)

        # Obtener estadísticas del día si se solicitan
        stats = None
        if include_stats:
            stats = await self._activity_service.get_day_activity_statistics(day_id)

        # Formatear fecha del día
        day_date = day.date.strftime("%Y-%m-%d")

        return ActivityDTOMapper.to_day_activities_response(
            day_id,
            day_date,
            activity_list_responses,
            stats
        )