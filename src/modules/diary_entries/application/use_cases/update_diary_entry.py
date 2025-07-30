from ..dtos.diary_entry_dto import UpdateDiaryEntryDTO, DiaryEntryResponseDTO, DiaryEntryDTOMapper
from ...domain.diary_entry_service import DiaryEntryService
from ...domain.diary_entry_events import DiaryEntryUpdatedEvent
from ...domain.interfaces.diary_entry_repository import IDiaryEntryRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from shared.events.event_bus import EventBus
from shared.errors.custom_errors import NotFoundError


class UpdateDiaryEntryUseCase:
    def __init__(
        self,
        diary_entry_repository: IDiaryEntryRepository,
        trip_member_repository: ITripMemberRepository,
        user_repository: IUserRepository,
        diary_entry_service: DiaryEntryService,
        event_bus: EventBus
    ):
        self._diary_entry_repository = diary_entry_repository
        self._trip_member_repository = trip_member_repository
        self._user_repository = user_repository
        self._diary_entry_service = diary_entry_service
        self._event_bus = event_bus

    async def execute(
        self, 
        entry_id: str, 
        dto: UpdateDiaryEntryDTO, 
        user_id: str
    ) -> DiaryEntryResponseDTO:
        entry = await self._diary_entry_repository.find_by_id(entry_id)
        if not entry or not entry.is_active():
            raise NotFoundError("Entrada de diario no encontrada")

        trip_id = await self._diary_entry_service.validate_entry_update(entry, user_id)

        updated_fields = []
        old_word_count = entry.get_word_count()
        
        if dto.content is not None:
            entry.update_content(dto.content)
            updated_fields.append("content")
        
        if dto.emotions is not None:
            entry.update_emotions(dto.emotions)
            updated_fields.append("emotions")

        updated_entry = await self._diary_entry_repository.update(entry)

        author_info = None
        author = await self._user_repository.find_by_id(entry.user_id)
        if author:
            author_info = {
                "id": author.id,
                "full_name": author.nombre,
                "avatar_url": author.url_foto_perfil
            }

        event = DiaryEntryUpdatedEvent(
            trip_id=trip_id,
            day_id=entry.day_id,
            entry_id=entry_id,
            user_id=user_id,
            updated_fields=updated_fields,
            old_word_count=old_word_count,
            new_word_count=updated_entry.get_word_count()
        )
        await self._event_bus.publish(event)

        return DiaryEntryDTOMapper.to_diary_entry_response(
            updated_entry.to_public_data(),
            can_edit=True,
            can_delete=True,
            author_info=author_info,
            word_count=updated_entry.get_word_count(),
            dominant_emotion=updated_entry.get_dominant_emotion()
        )