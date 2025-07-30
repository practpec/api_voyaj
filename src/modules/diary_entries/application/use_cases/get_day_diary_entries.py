from typing import List
from ..dtos.diary_entry_dto import DiaryEntryResponseDTO, DiaryEntryDTOMapper
from ...domain.diary_entry_service import DiaryEntryService
from ...domain.interfaces.diary_entry_repository import IDiaryEntryRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from modules.days.domain.interfaces.day_repository import IDayRepository
from shared.errors.custom_errors import NotFoundError, ForbiddenError


class GetDayDiaryEntriesUseCase:
    def __init__(
        self,
        diary_entry_repository: IDiaryEntryRepository,
        day_repository: IDayRepository,
        trip_member_repository: ITripMemberRepository,
        user_repository: IUserRepository,
        diary_entry_service: DiaryEntryService
    ):
        self._diary_entry_repository = diary_entry_repository
        self._day_repository = day_repository
        self._trip_member_repository = trip_member_repository
        self._user_repository = user_repository
        self._diary_entry_service = diary_entry_service

    async def execute(self, day_id: str, user_id: str) -> List[DiaryEntryResponseDTO]:
        day = await self._day_repository.find_by_id(day_id)
        if not day:
            raise NotFoundError("Día no encontrado")

        trip_member = await self._trip_member_repository.find_by_trip_and_user(
            day.trip_id, user_id
        )
        if not trip_member:
            raise ForbiddenError("No tienes acceso a este día")

        entries = await self._diary_entry_repository.find_by_day_id(day_id)

        user_permissions = {}
        authors_info = {}
        author_ids = set()

        for entry in entries:
            author_ids.add(entry.user_id)
            user_permissions[entry.id] = {
                "can_edit": entry.user_id == user_id,
                "can_delete": entry.user_id == user_id
            }

        for author_id in author_ids:
            author = await self._user_repository.find_by_id(author_id)
            if author:
                authors_info[author_id] = {
                    "id": author.id,
                    "full_name": author.nombre,
                    "avatar_url": author.url_foto_perfil
                }

        entries_data = [entry.to_public_data() for entry in entries]

        return DiaryEntryDTOMapper.to_diary_entries_list(
            entries_data,
            user_permissions=user_permissions,
            authors_info=authors_info
        )