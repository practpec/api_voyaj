from typing import List
from ..dtos.diary_entry_dto import DayDiaryEntriesResponseDTO, DiaryEntryListResponseDTO, DiaryEntryDTOMapper
from ...domain.diary_entry_service import DiaryEntryService
from ...domain.interfaces.diary_entry_repository import IDiaryEntryRepository
from modules.days.domain.interfaces.day_repository import IDayRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
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

    async def execute(
        self, 
        day_id: str, 
        user_id: str, 
        include_stats: bool = True
    ) -> DayDiaryEntriesResponseDTO:
        """Obtener todas las entradas de diario de un día específico"""
        
        # Validar que el día existe
        day = await self._day_repository.find_by_id(day_id)
        if not day or not day.is_active():
            raise NotFoundError("Día no encontrado")

        # Validar permisos del usuario para ver entradas del día
        has_permission = await self._diary_entry_service.validate_user_can_view_day_entries(
            day_id, 
            user_id
        )
        
        if not has_permission:
            raise ForbiddenError("No tienes permisos para ver las entradas de este día")

        # Obtener entradas del día
        entries = await self._diary_entry_repository.find_by_day_id(day_id)

        # Obtener información de autores únicos
        user_ids = list(set(entry.user_id for entry in entries))
        users_info = {}
        for uid in user_ids:
            user = await self._user_repository.find_by_id(uid)
            if user:
                users_info[uid] = {
                    "id": user.id,
                    "full_name": user.get_full_name(),
                    "avatar_url": user.avatar_url
                }

        # Mapear entradas a DTOs de respuesta
        entry_responses: List[DiaryEntryListResponseDTO] = []
        for entry in entries:
            can_edit = entry.can_be_edited_by(user_id)
            author_info = users_info.get(entry.user_id)

            entry_response = DiaryEntryDTOMapper.to_diary_entry_list_response(
                entry.to_public_data(),
                can_edit=can_edit,
                author_info=author_info,
                word_count=entry.get_word_count(),
                dominant_emotion=entry.get_dominant_emotion()
            )
            entry_responses.append(entry_response)

        # Obtener estadísticas si se solicitan
        stats = {}
        if include_stats:
            stats = await self._diary_entry_service.get_day_diary_statistics(day_id)

        # Crear respuesta completa
        return DiaryEntryDTOMapper.to_day_diary_entries_response(
            day_id=day_id,
            day_date=day._data.date.isoformat(),
            entries=entry_responses,
            stats=stats
        )