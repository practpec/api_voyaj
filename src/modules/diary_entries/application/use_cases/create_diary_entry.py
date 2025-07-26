from ..dtos.diary_entry_dto import CreateDiaryEntryDTO, DiaryEntryResponseDTO, DiaryEntryDTOMapper
from ...domain.diary_entry import DiaryEntry
from ...domain.diary_entry_service import DiaryEntryService
from ...domain.diary_entry_events import DiaryEntryCreatedEvent
from ...domain.interfaces.diary_entry_repository import IDiaryEntryRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from shared.events.event_bus import EventBus


class CreateDiaryEntryUseCase:
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

    async def execute(self, dto: CreateDiaryEntryDTO, user_id: str) -> DiaryEntryResponseDTO:
        """Crear nueva entrada de diario"""
        trip_id = await self._diary_entry_service.validate_entry_creation(
            dto.day_id,
            user_id,
            dto.content
        )

        # Crear entrada de diario
        diary_entry = DiaryEntry.create(
            day_id=dto.day_id,
            user_id=user_id,
            content=dto.content,
            emotions=dto.emotions
        )

        # Guardar en repositorio
        created_entry = await self._diary_entry_repository.create(diary_entry)

        # Obtener información del autor
        author_info = None
        author = await self._user_repository.find_by_id(user_id)
        if author:
            author_info = {
                "id": author.id,
                "full_name": author.get_full_name(),
                "avatar_url": author.avatar_url
            }

        # Emitir evento
        event = DiaryEntryCreatedEvent(
            trip_id=trip_id,
            day_id=dto.day_id,
            entry_id=created_entry.id,
            user_id=user_id,
            word_count=created_entry.get_word_count(),
            has_emotions=bool(created_entry.emotions)
        )
        await self._event_bus.publish(event)

        # Mapear a DTO de respuesta
        return DiaryEntryDTOMapper.to_diary_entry_response(
            created_entry.to_public_data(),
            can_edit=True,
            can_delete=True,
            author_info=author_info,
            word_count=created_entry.get_word_count(),
            dominant_emotion=created_entry.get_dominant_emotion()
        )