from typing import List, Optional
from datetime import time
from .activity import Activity, ActivityStatus
from .interfaces.activity_repository import IActivityRepository
from modules.days.domain.interfaces.day_repository import IDayRepository
from modules.trips.domain.interfaces.trip_repository import ITripRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from shared.errors.custom_errors import NotFoundError, ValidationError, ForbiddenError


class ActivityService:
    def __init__(
        self,
        activity_repository: IActivityRepository,
        day_repository: IDayRepository,
        trip_repository: ITripRepository,
        trip_member_repository: ITripMemberRepository
    ):
        self._activity_repository = activity_repository
        self._day_repository = day_repository
        self._trip_repository = trip_repository
        self._trip_member_repository = trip_member_repository

    async def validate_activity_creation(
        self,
        day_id: str,
        title: str,
        user_id: str,
        start_time: Optional[time] = None,
        end_time: Optional[time] = None
    ) -> str:
        """Validar creación de actividad y retornar trip_id"""
        if not title or len(title.strip()) < 2:
            raise ValidationError("El título debe tener al menos 2 caracteres")

        day = await self._day_repository.find_by_id(day_id)
        if not day or not day.is_active():
            raise NotFoundError("Día no encontrado")

        trip = await self._trip_repository.find_by_id(day.trip_id)
        if not trip or not trip.is_active():
            raise NotFoundError("Viaje no encontrado")

        await self._validate_user_permissions(trip.id, user_id, "create_activity")

        if start_time and end_time and start_time >= end_time:
            raise ValidationError("La hora de inicio debe ser anterior a la hora de fin")

        return trip.id

    async def validate_activity_update(
        self,
        activity: Activity,
        user_id: str
    ) -> str:
        """Validar actualización de actividad y retornar trip_id"""
        if not activity.is_active():
            raise ValidationError("No se puede actualizar una actividad eliminada")

        day = await self._day_repository.find_by_id(activity.day_id)
        if not day or not day.is_active():
            raise NotFoundError("Día no encontrado")

        trip_id = await self._validate_user_permissions(day.trip_id, user_id, "edit_activity")
        return trip_id

    async def validate_activity_deletion(
        self,
        activity: Activity,
        user_id: str
    ) -> str:
        """Validar eliminación de actividad y retornar trip_id"""
        if not activity.is_active():
            raise ValidationError("La actividad ya está eliminada")

        day = await self._day_repository.find_by_id(activity.day_id)
        if not day or not day.is_active():
            raise NotFoundError("Día no encontrado")

        trip_id = await self._validate_user_permissions(day.trip_id, user_id, "delete_activity")
        return trip_id

    async def validate_activity_status_change(
        self,
        activity: Activity,
        user_id: str,
        new_status: ActivityStatus
    ) -> str:
        """Validar cambio de estado de actividad y retornar trip_id"""
        if not activity.is_active():
            raise ValidationError("No se puede cambiar el estado de una actividad eliminada")

        day = await self._day_repository.find_by_id(activity.day_id)
        if not day or not day.is_active():
            raise NotFoundError("Día no encontrado")

        # Validaciones específicas por estado
        if new_status == ActivityStatus.IN_PROGRESS:
            if activity.status != ActivityStatus.PLANNED.value:
                raise ValidationError("Solo se pueden iniciar actividades planificadas")
        elif new_status == ActivityStatus.COMPLETED:
            if activity.status == ActivityStatus.CANCELLED.value:
                raise ValidationError("No se puede completar una actividad cancelada")
        elif new_status == ActivityStatus.CANCELLED:
            if activity.status == ActivityStatus.COMPLETED.value:
                raise ValidationError("No se puede cancelar una actividad completada")

        trip_id = await self._validate_user_permissions(day.trip_id, user_id, "change_activity_status")
        return trip_id

    async def _validate_user_permissions(
        self,
        trip_id: str,
        user_id: str,
        action: str
    ) -> str:
        """Validar permisos del usuario en el viaje"""
        member = await self._trip_member_repository.find_by_trip_and_user(trip_id, user_id)
        if not member:
            raise ForbiddenError("No eres miembro de este viaje")

        # Definir qué roles pueden realizar qué acciones
        if action in ["create_activity", "edit_activity", "delete_activity"]:
            if not member.can_edit_trip():
                raise ForbiddenError("No tienes permisos para gestionar actividades")
        elif action in ["change_activity_status"]:
            # Los miembros regulares pueden cambiar estados de actividades
            if not member.is_active():
                raise ForbiddenError("No tienes acceso activo a este viaje")

        return trip_id

    async def reorder_activities(
        self,
        day_id: str,
        activity_orders: List[dict],  # [{"activity_id": str, "order": int}]
        user_id: str
    ) -> List[Activity]:
        """Reordenar actividades de un día"""
        day = await self._day_repository.find_by_id(day_id)
        if not day or not day.is_active():
            raise NotFoundError("Día no encontrado")

        await self._validate_user_permissions(day.trip_id, user_id, "edit_activity")

        activities = []
        for item in activity_orders:
            activity = await self._activity_repository.find_by_id(item["activity_id"])
            if not activity or not activity.is_active() or activity.day_id != day_id:
                raise ValidationError(f"Actividad {item['activity_id']} no válida para este día")
            
            activity.update_order(item["order"])
            updated_activity = await self._activity_repository.update(activity)
            activities.append(updated_activity)

        return activities

    async def can_user_access_activity(
        self,
        activity: Activity,
        user_id: str
    ) -> bool:
        """Verificar si usuario puede acceder a la actividad"""
        try:
            day = await self._day_repository.find_by_id(activity.day_id)
            if not day:
                return False

            member = await self._trip_member_repository.find_by_trip_and_user(day.trip_id, user_id)
            return member is not None
        except:
            return False

   
    async def get_trip_activity_summary(
        self,
        trip_id: str
    ) -> dict:
        """Obtener resumen de actividades del viaje completo"""
        activities = await self._activity_repository.find_by_trip_id(trip_id)
        
        total_activities = len(activities)
        completed_activities = len([a for a in activities if a.is_completed()])
        
        categories = {}
        for activity in activities:
            category = activity.category
            if category not in categories:
                categories[category] = 0
            categories[category] += 1
        
        return {
            "total_activities": total_activities,
            "completed_activities": completed_activities,
            "completion_percentage": (completed_activities / total_activities * 100) if total_activities > 0 else 0,
            "activities_by_category": categories
        }
    
    # src/modules/activities/domain/activity_service.py (métodos faltantes)

    async def get_day_activity_statistics(self, day_id: str) -> dict:
        """Obtener estadísticas de actividades del día"""
        activities = await self._activity_repository.find_by_day_id_ordered(day_id)
        
        total_activities = len(activities)
        planned_count = len([a for a in activities if a.status == ActivityStatus.PLANNED.value])
        in_progress_count = len([a for a in activities if a.status == ActivityStatus.IN_PROGRESS.value])
        completed_count = len([a for a in activities if a.status == ActivityStatus.COMPLETED.value])
        cancelled_count = len([a for a in activities if a.status == ActivityStatus.CANCELLED.value])
        
        # Calcular costos
        estimated_cost = sum(a.estimated_cost or 0 for a in activities)
        actual_cost = sum(a.actual_cost or 0 for a in activities if a.actual_cost is not None)
        
        # Progreso del día (actividades completadas / total)
        progress_percentage = (completed_count / total_activities * 100) if total_activities > 0 else 0
        
        return {
            "total_activities": total_activities,
            "planned": planned_count,
            "in_progress": in_progress_count,
            "completed": completed_count,
            "cancelled": cancelled_count,
            "estimated_cost": estimated_cost,
            "actual_cost": actual_cost,
            "progress_percentage": round(progress_percentage, 2)
        }
    
    # También agregar el permiso "view_activities" en _validate_user_permissions
    async def _validate_user_permissions(
        self,
        trip_id: str,
        user_id: str,
        action: str
    ) -> str:
        """Validar permisos del usuario en el viaje"""
        member = await self._trip_member_repository.find_by_trip_and_user(trip_id, user_id)
        if not member:
            raise ForbiddenError("No eres miembro de este viaje")
    
        # Definir qué roles pueden realizar qué acciones
        if action in ["create_activity", "edit_activity", "delete_activity"]:
            if not member.can_edit_trip():
                raise ForbiddenError("No tienes permisos para gestionar actividades")
        elif action in ["change_activity_status", "view_activities"]:
            # Los miembros regulares pueden cambiar estados y ver actividades
            if not member.is_active():
                raise ForbiddenError("No tienes acceso activo a este viaje")
    
        return trip_id
    