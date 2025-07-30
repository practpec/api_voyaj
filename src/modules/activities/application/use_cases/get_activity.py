# src/modules/activities/application/use_cases/get_activity.py
from ..dtos.activity_dto import ActivityResponseDTO, ActivityDTOMapper
from ...domain.activity_service import ActivityService
from ...domain.interfaces.activity_repository import IActivityRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from modules.days.domain.interfaces.day_repository import IDayRepository
from shared.errors.custom_errors import NotFoundError, ForbiddenError


class GetActivityUseCase:
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

    async def execute(self, activity_id: str, user_id: str) -> ActivityResponseDTO:
        """Obtener actividad por ID"""
        # Buscar actividad
        activity = await self._activity_repository.find_by_id(activity_id)
        if not activity or not activity.is_active():
            raise NotFoundError("Actividad no encontrada")

        # Verificar permisos en el viaje
        trip_member = await self._trip_member_repository.find_by_trip_and_user(
            activity.trip_id, user_id
        )
        if not trip_member:
            raise ForbiddenError("No tienes acceso a esta actividad")

        return ActivityDTOMapper.to_activity_response(activity.to_public_data())