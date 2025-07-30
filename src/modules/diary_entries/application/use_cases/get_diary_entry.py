from ..dtos.diary_entry_dto import DiaryEntryResponseDTO, DiaryEntryDTOMapper
from ...domain.diary_entry_service import DiaryEntryService
from ...domain.interfaces.diary_entry_repository import IDiaryEntryRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from shared.errors.custom_errors import NotFoundError, ForbiddenError


class GetDiaryEntryUseCase:
    def __init__(
        self,
        diary_entry_repository: IDiaryEntryRepository,
        trip_member_repository: ITripMemberRepository,
        user_repository: IUserRepository,
        diary_entry_service: DiaryEntryService
    ):
        self._diary_entry_repository = diary_entry_repository
        self._trip_member_repository = trip_member_repository
        self._user_repository = user_repository
        self._diary_entry_service = diary_entry_service

    async def execute(self, entry_id: str, user_id: str) -> DiaryEntryResponseDTO:
        entry = await self._diary_entry_repository.find_by_id(entry_id)
        if not entry or not entry.is_active():
            raise NotFoundError("Entrada de diario no encontrada")

        trip_id = await self._diary_entry_service.validate_entry_access(entry, user_id)

        author_info = None
        author = await self._user_repository.find_by_id(entry.user_id)
        if author:
            author_info = {
                "id": author.id,
                "full_name": author.nombre,
                "avatar_url": author.url_foto_perfil
            }

        can_edit = entry.user_id == user_id
        can_delete = entry.user_id == user_id

        return DiaryEntryDTOMapper.to_diary_entry_response(
            entry.to_public_data(),
            can_edit=can_edit,
            can_delete=can_delete,
            author_info=author_info,
            word_count=entry.get_word_count(),
            dominant_emotion=entry.get_dominant_emotion()
        )