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
        """Obtener detalles de una entrada de diario específica"""
        entry = await self._diary_entry_repository.find_by_id(entry_id)
        if not entry or not entry.is_active():
            raise NotFoundError("Entrada de diario no encontrada")

        # Validar permisos del usuario para ver la entrada
        has_permission = await self._diary_entry_service.validate_user_can_view_entry(
            entry, 
            user_id
        )
        
        if not has_permission:
            raise ForbiddenError("No tienes permisos para ver esta entrada")

        # Obtener información del autor
        author_info = None
        if entry.user_id:
            author = await self._user_repository.find_by_id(entry.user_id)
            if author:
                author_info = {
                    "id": author.id,
                    "full_name": author.get_full_name(),
                    "avatar_url": author.avatar_url
                }

        # Determinar permisos del usuario actual
        can_edit = entry.can_be_edited_by(user_id)
        can_delete = entry.can_be_edited_by(user_id)

        return DiaryEntryDTOMapper.to_diary_entry_response(
            entry.to_public_data(),
            can_edit=can_edit,
            can_delete=can_delete,
            author_info=author_info,
            word_count=entry.get_word_count(),
            dominant_emotion=entry.get_dominant_emotion()
        )