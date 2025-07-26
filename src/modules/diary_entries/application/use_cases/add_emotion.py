from ..dtos.diary_entry_dto import AddEmotionDTO, DiaryEntryResponseDTO, DiaryEntryDTOMapper
from ...domain.diary_entry_service import DiaryEntryService
from ...domain.diary_entry_events import DiaryEntryEmotionsUpdatedEvent
from ...domain.interfaces.diary_entry_repository import IDiaryEntryRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from shared.events.event_bus import EventBus
from shared.errors.custom_errors import NotFoundError


class AddEmotionUseCase:
    def __init__(
        self,
        diary_entry_repository: IDiaryEntryRepository,
        user_repository: IUserRepository,
        diary_entry_service: DiaryEntryService,
        event_bus: EventBus
    ):
        self._diary_entry_repository = diary_entry_repository
        self._user_repository = user_repository
        self._diary_entry_service = diary_entry_service
        self._event_bus = event_bus

    async def execute(
        self, 
        entry_id: str, 
        dto: AddEmotionDTO, 
        user_id: str
    ) -> DiaryEntryResponseDTO:
        """Agregar emoción a una entrada de diario"""
        entry = await self._diary_entry_repository.find_by_id(entry_id)
        if not entry or not entry.is_active():
            raise NotFoundError("Entrada de diario no encontrada")

        trip_id = await self._diary_entry_service.validate_entry_update(entry, user_id)

        # Agregar emoción
        entry.add_emotion(
            emotion_type=dto.emotion_type,
            intensity=dto.intensity,
            note=dto.note
        )

        # Actualizar en repositorio
        updated_entry = await self._diary_entry_repository.update(entry)

        # Obtener información del autor
        author_info = None
        author = await self._user_repository.find_by_id(entry.user_id)
        if author:
            author_info = {
                "id": author.id,
                "full_name": author.get_full_name(),
                "avatar_url": author.avatar_url
            }

        # Contar emociones
        emotions_count = 0
        if entry.emotions and "emotions" in entry.emotions:
            emotions_count = len(entry.emotions["emotions"])

        # Emitir evento
        event = DiaryEntryEmotionsUpdatedEvent(
            trip_id=trip_id,
            day_id=entry.day_id,
            entry_id=entry_id,
            user_id=user_id,
            dominant_emotion=updated_entry.get_dominant_emotion(),
            emotions_count=emotions_count
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