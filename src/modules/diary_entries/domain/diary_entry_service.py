from typing import Optional
from .diary_entry import DiaryEntry
from .interfaces.diary_entry_repository import IDiaryEntryRepository
from modules.days.domain.interfaces.day_repository import IDayRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from shared.errors.custom_errors import ValidationError, NotFoundError, ForbiddenError


class DiaryEntryService:
    def __init__(
        self,
        diary_entry_repository: IDiaryEntryRepository,
        day_repository: IDayRepository,
        trip_member_repository: ITripMemberRepository
    ):
        self._diary_entry_repository = diary_entry_repository
        self._day_repository = day_repository
        self._trip_member_repository = trip_member_repository

    async def validate_entry_creation(
        self, 
        day_id: str, 
        user_id: str, 
        content: str
    ) -> str:
        if not content or not content.strip():
            raise ValidationError("El contenido no puede estar vacío")

        if len(content.strip()) < 10:
            raise ValidationError("El contenido debe tener al menos 10 caracteres")

        day = await self._day_repository.find_by_id(day_id)
        if not day:
            raise NotFoundError("Día no encontrado")

        trip_member = await self._trip_member_repository.find_by_trip_and_user(
            day.trip_id, user_id
        )
        if not trip_member:
            raise ForbiddenError("No tienes permisos para crear entradas en este día")

        existing_entry = await self._diary_entry_repository.find_by_user_and_day(
            user_id, day_id
        )
        if existing_entry and existing_entry.is_active():
            raise ValidationError("Ya tienes una entrada de diario para este día")

        return day.trip_id

    async def validate_entry_access(self, entry: DiaryEntry, user_id: str) -> str:
        day = await self._day_repository.find_by_id(entry.day_id)
        if not day:
            raise NotFoundError("Día no encontrado")

        trip_member = await self._trip_member_repository.find_by_trip_and_user(
            day.trip_id, user_id
        )
        if not trip_member:
            raise ForbiddenError("No tienes acceso a esta entrada")

        return day.trip_id

    async def validate_entry_update(self, entry: DiaryEntry, user_id: str) -> str:
        if entry.user_id != user_id:
            raise ForbiddenError("Solo puedes editar tus propias entradas")

        day = await self._day_repository.find_by_id(entry.day_id)
        if not day:
            raise NotFoundError("Día no encontrado")

        trip_member = await self._trip_member_repository.find_by_trip_and_user(
            day.trip_id, user_id
        )
        if not trip_member:
            raise ForbiddenError("No tienes permisos para editar esta entrada")

        return day.trip_id

    async def validate_entry_deletion(self, entry: DiaryEntry, user_id: str) -> str:
        if entry.user_id != user_id:
            raise ForbiddenError("Solo puedes eliminar tus propias entradas")

        day = await self._day_repository.find_by_id(entry.day_id)
        if not day:
            raise NotFoundError("Día no encontrado")

        trip_member = await self._trip_member_repository.find_by_trip_and_user(
            day.trip_id, user_id
        )
        if not trip_member:
            raise ForbiddenError("No tienes permisos para eliminar esta entrada")

        return day.trip_id

    async def can_user_create_entry_for_day(self, day_id: str, user_id: str) -> bool:
        try:
            await self.validate_entry_creation(day_id, user_id, "contenido de prueba")
            return True
        except (ValidationError, NotFoundError, ForbiddenError):
            return False

    async def get_user_entries_count_for_trip(self, trip_id: str, user_id: str) -> int:
        return await self._diary_entry_repository.count_by_user_and_trip(user_id, trip_id)

    async def has_user_entry_for_day(self, day_id: str, user_id: str) -> bool:
        entry = await self._diary_entry_repository.find_by_user_and_day(user_id, day_id)
        return entry is not None and entry.is_active()