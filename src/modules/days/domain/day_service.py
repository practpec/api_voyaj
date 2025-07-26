from typing import List, Optional
from datetime import date, datetime
from .Day import Day
from .interfaces.day_repository import IDayRepository
from modules.trips.domain.interfaces.trip_repository import ITripRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from shared.errors.custom_errors import NotFoundError, ValidationError, ForbiddenError


class DayService:
    def __init__(
        self,
        day_repository: IDayRepository,
        trip_repository: ITripRepository,
        trip_member_repository: ITripMemberRepository
    ):
        self._day_repository = day_repository
        self._trip_repository = trip_repository
        self._trip_member_repository = trip_member_repository

    async def validate_day_creation(
        self,
        trip_id: str,
        day_date: date,
        user_id: str
    ) -> None:
        """Validar creación de día"""
        trip = await self._trip_repository.find_by_id(trip_id)
        if not trip or not trip.is_active():
            raise NotFoundError("Viaje no encontrado")

        member = await self._trip_member_repository.find_by_trip_and_user(trip_id, user_id)
        if not member or not member.can_edit_trip():
            raise ForbiddenError("No tienes permisos para crear días en este viaje")

        if day_date < trip.start_date.date() or day_date > trip.end_date.date():
            raise ValidationError("La fecha del día debe estar dentro del rango del viaje")

        existing_day = await self._day_repository.find_by_trip_and_date(trip_id, day_date)
        if existing_day:
            raise ValidationError("Ya existe un día para esta fecha")

    async def validate_day_update(
        self,
        day: Day,
        user_id: str
    ) -> None:
        """Validar actualización de día"""
        if not day.is_active():
            raise ValidationError("No se puede actualizar un día eliminado")

        member = await self._trip_member_repository.find_by_trip_and_user(day.trip_id, user_id)
        if not member or not member.can_edit_trip():
            raise ForbiddenError("No tienes permisos para actualizar este día")

    async def validate_day_deletion(
        self,
        day: Day,
        user_id: str
    ) -> None:
        """Validar eliminación de día"""
        if not day.is_active():
            raise ValidationError("El día ya está eliminado")

        member = await self._trip_member_repository.find_by_trip_and_user(day.trip_id, user_id)
        if not member or not member.can_edit_trip():
            raise ForbiddenError("No tienes permisos para eliminar este día")

    async def generate_trip_days(
        self,
        trip_id: str,
        user_id: str
    ) -> List[Day]:
        """Generar días automáticamente para todo el viaje"""
        trip = await self._trip_repository.find_by_id(trip_id)
        if not trip or not trip.is_active():
            raise NotFoundError("Viaje no encontrado")

        member = await self._trip_member_repository.find_by_trip_and_user(trip_id, user_id)
        if not member or not member.can_edit_trip():
            raise ForbiddenError("No tienes permisos para generar días")

        existing_days = await self._day_repository.find_by_trip_id(trip_id)
        existing_dates = {day.date for day in existing_days}

        days_to_create = []
        current_date = trip.start_date.date()
        end_date = trip.end_date.date()

        while current_date <= end_date:
            if current_date not in existing_dates:
                day = Day.create(trip_id, current_date)
                days_to_create.append(day)
            current_date = current_date.replace(day=current_date.day + 1)

        return days_to_create

    async def get_trip_timeline(
        self,
        trip_id: str,
        user_id: str
    ) -> List[Day]:
        """Obtener timeline completo del viaje"""
        member = await self._trip_member_repository.find_by_trip_and_user(trip_id, user_id)
        if not member:
            raise ForbiddenError("No tienes acceso a este viaje")

        return await self._day_repository.find_by_trip_id_ordered(trip_id)

    async def can_user_access_day(
        self,
        day: Day,
        user_id: str
    ) -> bool:
        """Verificar si usuario puede acceder al día"""
        member = await self._trip_member_repository.find_by_trip_and_user(day.trip_id, user_id)
        return member is not None

    async def get_day_statistics(
        self,
        trip_id: str
    ) -> dict:
        """Obtener estadísticas de días del viaje"""
        days = await self._day_repository.find_by_trip_id(trip_id)
        
        total_days = len(days)
        days_with_notes = len([day for day in days if day.notes])
        
        return {
            "total_days": total_days,
            "days_with_notes": days_with_notes,
            "completion_percentage": (days_with_notes / total_days * 100) if total_days > 0 else 0
        }