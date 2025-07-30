from ..dtos.diary_entry_dto import DiaryEntryStatsDTO
from ...domain.diary_entry_service import DiaryEntryService
from ...domain.interfaces.diary_entry_repository import IDiaryEntryRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from modules.trips.domain.interfaces.trip_repository import ITripRepository
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

    async def execute(self, trip_id: str, user_id: str) -> DiaryEntryStatsDTO:
        trip = await self._trip_repository.find_by_id(trip_id)
        if not trip:
            raise NotFoundError("Viaje no encontrado")

        trip_member = await self._trip_member_repository.find_by_trip_and_user(
            trip_id, user_id
        )
        if not trip_member:
            raise ForbiddenError("No tienes acceso a este viaje")

        stats = await self._diary_entry_repository.get_trip_diary_statistics(trip_id)

        return DiaryEntryStatsDTO(
            total_entries=stats.get("total_entries", 0),
            total_words=stats.get("total_words", 0),
            average_words_per_entry=stats.get("average_words_per_entry", 0.0),
            most_common_emotion=stats.get("most_common_emotion"),
            entries_with_emotions=stats.get("entries_with_emotions", 0),
            entries_by_day=stats.get("entries_by_day", {}),
            emotion_distribution=stats.get("emotion_distribution", {})
        )