from ..dtos.day_dto import DayResponseDTO, DayDTOMapper
from ...domain.day_service import DayService
from ...domain.interfaces.day_repository import IDayRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from shared.errors.custom_errors import NotFoundError, ForbiddenError


class GetDayUseCase:
    def __init__(
        self,
        day_repository: IDayRepository,
        trip_member_repository: ITripMemberRepository,
        day_service: DayService
    ):
        self._day_repository = day_repository
        self._trip_member_repository = trip_member_repository
        self._day_service = day_service

    async def execute(self, day_id: str, user_id: str) -> DayResponseDTO:
        """Obtener día específico por ID"""
        day = await self._day_repository.find_by_id(day_id)
        if not day or not day.is_active():
            raise NotFoundError("Día no encontrado")

        can_access = await self._day_service.can_user_access_day(day, user_id)
        if not can_access:
            raise ForbiddenError("No tienes acceso a este día")

        member = await self._trip_member_repository.find_by_trip_and_user(day.trip_id, user_id)
        can_edit = member.can_edit_trip() if member else False

        # TODO: Implementar conteo de actividades y fotos cuando estén disponibles
        activity_count = 0
        photo_count = 0

        return DayDTOMapper.to_day_response(
            day.to_public_data(),
            can_edit=can_edit,
            activity_count=activity_count,
            photo_count=photo_count
        )