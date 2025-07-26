from ..dtos.diary_entry_dto import TripDiaryStatsDTO, DiaryEntryDTOMapper
from ...domain.diary_entry_service import DiaryEntryService
from ...domain.interfaces.diary_entry_repository import IDiaryEntryRepository
from modules.trips.domain.interfaces.trip_repository import ITripRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from shared.errors.custom_errors import NotFoundError, ForbiddenError


class GetTripDiaryStatsUseCase:
    def __init__(
        self,
        diary_entry_repository: IDiaryEntryRepository,
        trip_repository: ITripRepository,
        trip_member_repository: ITripMemberRepository,
        diary_entry_service: DiaryEntryService
    ):
        self._diary_entry_repository = diary_entry_repository
        self._trip_repository = trip_repository
        self._trip_member_repository = trip_member_repository
        self._diary_entry_service = diary_entry_service

    async def execute(self, trip_id: str, user_id: str) -> TripDiaryStatsDTO:
        """Obtener estadísticas del diario del viaje completo"""
        
        # Validar que el viaje existe
        trip = await self._trip_repository.find_by_id(trip_id)
        if not trip or not trip.is_active():
            raise NotFoundError("Viaje no encontrado")

        # Validar permisos del usuario
        member = await self._trip_member_repository.find_by_trip_and_user(trip_id, user_id)
        if not member:
            raise ForbiddenError("No eres miembro de este viaje")

        # Obtener estadísticas del diario del viaje
        stats = await self._diary_entry_service.get_trip_diary_summary(trip_id)
        stats["trip_id"] = trip_id

        return DiaryEntryDTOMapper.to_trip_diary_stats(stats)