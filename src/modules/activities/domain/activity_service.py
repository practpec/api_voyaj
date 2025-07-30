# src/modules/activities/domain/activity_service.py
from typing import List, Dict, Any, Optional
from .activity import Activity
from .interfaces.activity_repository import IActivityRepository
from modules.days.domain.Day import Day
from shared.errors.custom_errors import ValidationError, BusinessRuleError


class ActivityService:
    def __init__(self, activity_repository: IActivityRepository):
        self._activity_repository = activity_repository

    async def validate_activity_creation(
         self, 
         dto, 
         day: Day
     ) -> None:
         """Validar creación de actividad"""
         # Validar título
         if not dto.title or len(dto.title.strip()) < 3:
             raise ValidationError("El título debe tener al menos 3 caracteres")
 
         # Validar categoría
         valid_categories = [
             "cultural", "adventure", "food", "shopping", "transport", 
             "accommodation", "entertainment", "nature", "sports", "other"
         ]
         if dto.category not in valid_categories:
             raise ValidationError(f"Categoría inválida. Debe ser una de: {', '.join(valid_categories)}")
 
         # Validar prioridad
         valid_priorities = ["low", "medium", "high", "critical"]
         if dto.priority not in valid_priorities:
             raise ValidationError(f"Prioridad inválida. Debe ser una de: {', '.join(valid_priorities)}")
 
         # Validar duración estimada
         if dto.estimated_duration is not None and dto.estimated_duration <= 0:
             raise ValidationError("La duración estimada debe ser mayor a 0 minutos")
 
         # Validar costo estimado
         if dto.estimated_cost is not None and dto.estimated_cost < 0:
             raise ValidationError("El costo estimado no puede ser negativo")
 
         # Validar límite de actividades por día
         activity_count = await self._activity_repository.count_by_day_id(day.id)
         if activity_count >= 20:  # Límite máximo de actividades por día
             raise BusinessRuleError("No se pueden crear más de 20 actividades por día")
         
         
    async def validate_activity_update(self, activity: Activity, **update_fields) -> None:
        """Validar actualización de actividad"""
        # Verificar si la actividad puede ser editada
        if not activity.can_be_edited():
            raise BusinessRuleError("Esta actividad no puede ser editada en su estado actual")

        # Validar título si se está actualizando
        if "title" in update_fields:
            title = update_fields["title"]
            if not title or len(title.strip()) < 3:
                raise ValidationError("El título debe tener al menos 3 caracteres")

        # Validar categoría si se está actualizando
        if "category" in update_fields:
            category = update_fields["category"]
            valid_categories = [
                "cultural", "adventure", "food", "shopping", "transport", 
                "accommodation", "entertainment", "nature", "sports", "other"
            ]
            if category not in valid_categories:
                raise ValidationError(f"Categoría inválida. Debe ser una de: {', '.join(valid_categories)}")

        # Validar rating si se está actualizando
        if "rating" in update_fields:
            rating = update_fields["rating"]
            if rating is not None and not (1 <= rating <= 5):
                raise ValidationError("La calificación debe estar entre 1 y 5")

        # Validar costos reales
        if "actual_cost" in update_fields:
            actual_cost = update_fields["actual_cost"]
            if actual_cost is not None and actual_cost < 0:
                raise ValidationError("El costo real no puede ser negativo")

    async def validate_status_change(
        self, 
        activity: Activity, 
        new_status: str, 
        user_id: str
    ) -> None:
        """Validar cambio de estado"""
        valid_statuses = ["pending", "in_progress", "completed", "cancelled", "skipped"]
        if new_status not in valid_statuses:
            raise ValidationError(f"Estado inválido. Debe ser uno de: {', '.join(valid_statuses)}")

        current_status = activity.status

        # Reglas de transición de estados
        valid_transitions = {
            "pending": ["in_progress", "cancelled", "skipped"],
            "in_progress": ["completed", "cancelled", "pending"],
            "completed": [],  # No se puede cambiar desde completado
            "cancelled": ["pending"],
            "skipped": ["pending"]
        }

        if new_status not in valid_transitions.get(current_status, []):
            raise BusinessRuleError(
                f"No se puede cambiar de '{current_status}' a '{new_status}'"
            )

    async def validate_activity_reorder(
        self, 
        day_id: str, 
        activity_orders: List[Dict[str, Any]]
    ) -> None:
        """Validar reordenamiento de actividades"""
        if not activity_orders:
            raise ValidationError("La lista de órdenes no puede estar vacía")

        # Verificar que todos los elementos tengan la estructura correcta
        for i, order_item in enumerate(activity_orders):
            if not isinstance(order_item, dict):
                raise ValidationError(f"El elemento {i} debe ser un objeto")
            
            if "activity_id" not in order_item or "order" not in order_item:
                raise ValidationError(f"El elemento {i} debe tener 'activity_id' y 'order'")
            
            try:
                order_value = int(order_item["order"])
                if order_value < 1:
                    raise ValidationError(f"El orden del elemento {i} debe ser mayor a 0")
            except (ValueError, TypeError):
                raise ValidationError(f"El orden del elemento {i} debe ser un número entero")

        # Verificar que no haya IDs duplicados
        activity_ids = [item["activity_id"] for item in activity_orders]
        if len(activity_ids) != len(set(activity_ids)):
            raise ValidationError("No puede haber IDs de actividad duplicados")

        # Verificar que no haya órdenes duplicados
        orders = [item["order"] for item in activity_orders]
        if len(orders) != len(set(orders)):
            raise ValidationError("No puede haber números de orden duplicados")

    async def validate_activity_deletion(self, activity: Activity, user_id: str) -> None:
        """Validar eliminación de actividad"""
        if activity.status == "in_progress":
            raise BusinessRuleError("No se puede eliminar una actividad que está en progreso")

    async def get_next_activity_order(self, day_id: str) -> int:
        """Obtener el siguiente número de orden para una nueva actividad"""
        activities = await self._activity_repository.find_by_day_id_ordered(day_id)
        
        if not activities:
            return 1
        
        # Obtener el orden máximo y sumar 1
        max_order = max(activity.order for activity in activities)
        return max_order + 1

    async def generate_day_stats(self, activities: List[Activity]) -> Dict[str, Any]:
        """Generar estadísticas de actividades del día"""
        if not activities:
            return {
                "total_activities": 0,
                "completed_activities": 0,
                "pending_activities": 0,
                "cancelled_activities": 0,
                "total_estimated_cost": 0.0,
                "total_actual_cost": 0.0,
                "total_estimated_duration": 0,
                "total_actual_duration": 0,
                "activities_by_category": {},
                "activities_by_priority": {}
            }

        # Contadores básicos
        total = len(activities)
        completed = sum(1 for a in activities if a.status == "completed")
        pending = sum(1 for a in activities if a.status == "pending")
        cancelled = sum(1 for a in activities if a.status in ["cancelled", "skipped"])

        # Costos
        total_estimated_cost = sum(
            a.to_dict().get("estimated_cost", 0) or 0 for a in activities
        )
        total_actual_cost = sum(
            a.to_dict().get("actual_cost", 0) or 0 for a in activities
        )

        # Duración
        total_estimated_duration = sum(
            a.to_dict().get("estimated_duration", 0) or 0 for a in activities
        )
        total_actual_duration = sum(
            a.to_dict().get("actual_duration", 0) or 0 for a in activities
        )

        # Agrupaciones
        categories = {}
        priorities = {}
        
        for activity in activities:
            data = activity.to_dict()
            
            # Por categoría
            category = data.get("category", "other")
            categories[category] = categories.get(category, 0) + 1
            
            # Por prioridad
            priority = data.get("priority", "medium")
            priorities[priority] = priorities.get(priority, 0) + 1

        return {
            "total_activities": total,
            "completed_activities": completed,
            "pending_activities": pending,
            "cancelled_activities": cancelled,
            "total_estimated_cost": total_estimated_cost,
            "total_actual_cost": total_actual_cost,
            "total_estimated_duration": total_estimated_duration,
            "total_actual_duration": total_actual_duration,
            "activities_by_category": categories,
            "activities_by_priority": priorities
        }