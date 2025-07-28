# src/modules/days/domain/day_service.py - COMPLETO
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
            raise ValidationError("Ya existe un día para esta fecha en el viaje")

    async def validate_day_update(self, day: Day, user_id: str) -> None:
        """Validar actualización de día"""
        member = await self._trip_member_repository.find_by_trip_and_user(day.trip_id, user_id)
        if not member or not member.can_edit_trip():
            raise ForbiddenError("No tienes permisos para actualizar días en este viaje")

    async def validate_day_deletion(self, day: Day, user_id: str) -> None:
        """Validar eliminación de día"""
        member = await self._trip_member_repository.find_by_trip_and_user(day.trip_id, user_id)
        if not member or not member.can_edit_trip():
            raise ForbiddenError("No tienes permisos para eliminar días en este viaje")

    async def can_user_access_day(self, day: Day, user_id: str) -> bool:
        """Verificar si el usuario puede acceder al día"""
        try:
            # Verificar si el usuario es miembro del viaje
            member = await self._trip_member_repository.find_by_trip_and_user(day.trip_id, user_id)
            if not member:
                return False
            
            # Verificar que el miembro esté activo
            return member.is_active()
        
        except Exception as e:
            print(f"[ERROR] Error verificando acceso al día: {str(e)}")
            return False

    async def get_day_statistics(self, trip_id: str) -> dict:
        """Obtener estadísticas de días del viaje"""
        try:
            return await self._day_repository.get_trip_day_statistics(trip_id)
        except Exception as e:
            print(f"[ERROR] Error obteniendo estadísticas: {str(e)}")
            return {"total_days": 0, "days_with_notes": 0, "completion_percentage": 0.0}

    async def get_trip_timeline(self, trip_id: str, user_id: str) -> List[Day]:
        """Obtener timeline de días del viaje"""
        try:
            # Verificar que el usuario tenga acceso al viaje
            member = await self._trip_member_repository.find_by_trip_and_user(trip_id, user_id)
            if not member or not member.is_active():
                raise ForbiddenError("No tienes acceso a este viaje")
            
            # Obtener todos los días del viaje ordenados por fecha
            days = await self._day_repository.find_by_trip_id_ordered(trip_id)
            
            return days
        
        except Exception as e:
            print(f"[ERROR] Error obteniendo timeline: {str(e)}")
            raise e

    async def validate_trip_access(self, trip_id: str, user_id: str) -> None:
        """Validar que el usuario tenga acceso al viaje"""
        member = await self._trip_member_repository.find_by_trip_and_user(trip_id, user_id)
        if not member or not member.is_active():
            raise ForbiddenError("No tienes acceso a este viaje")

    async def can_user_edit_trip(self, trip_id: str, user_id: str) -> bool:
        """Verificar si el usuario puede editar el viaje"""
        try:
            member = await self._trip_member_repository.find_by_trip_and_user(trip_id, user_id)
            return member and member.can_edit_trip()
        except Exception as e:
            print(f"[ERROR] Error verificando permisos de edición: {str(e)}")
            return False

    async def generate_days_for_trip(self, trip_id: str, user_id: str) -> List[Day]:
        """Generar automáticamente todos los días para un viaje"""
        try:
            # Verificar permisos
            await self.validate_trip_access(trip_id, user_id)
            
            if not await self.can_user_edit_trip(trip_id, user_id):
                raise ForbiddenError("No tienes permisos para generar días en este viaje")

            # Obtener el viaje
            trip = await self._trip_repository.find_by_id(trip_id)
            if not trip or not trip.is_active():
                raise NotFoundError("Viaje no encontrado")

            # Obtener días existentes
            existing_days = await self._day_repository.find_by_trip_id(trip_id)
            existing_dates = {day.date for day in existing_days}

            # Generar días faltantes
            days_to_create = []
            current_date = trip.start_date.date()
            end_date = trip.end_date.date()
            
            from datetime import timedelta  # ✅ Import correcto

            while current_date <= end_date:
                if current_date not in existing_dates:
                    day = Day.create(
                        trip_id=trip_id,
                        date=current_date,
                        notes=f"Día {len(days_to_create) + 1} del viaje"
                    )
                    days_to_create.append(day)
                
                current_date = current_date + timedelta(days=1)  # ✅ Fix del bug

            # Crear días en lote si hay alguno
            if days_to_create:
                created_days = await self._day_repository.bulk_create(days_to_create)
                return created_days
            
            return []

        except Exception as e:
            print(f"[ERROR] Error generando días: {str(e)}")
            raise e