from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import uuid


@dataclass
class PlanRealityDifferenceData:
    """Entidad que representa diferencias entre plan y realidad"""
    id: str
    trip_id: str
    day_id: Optional[str]
    activity_id: Optional[str]
    metric: str
    planned_value: str
    actual_value: str
    notes: Optional[str]
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        trip_id: str,
        metric: str,
        planned_value: str,
        actual_value: str,
        notes: Optional[str] = None,
        day_id: Optional[str] = None,
        activity_id: Optional[str] = None
    ) -> 'PlanRealityDifferenceData':
        """Crear nueva diferencia plan vs realidad"""
        now = datetime.utcnow()
        
        return cls(
            id=str(uuid.uuid4()),
            trip_id=trip_id,
            day_id=day_id,
            activity_id=activity_id,
            metric=metric,
            planned_value=planned_value,
            actual_value=actual_value,
            notes=notes,
            is_deleted=False,
            created_at=now,
            updated_at=now
        )

    def update(
        self,
        metric: Optional[str] = None,
        planned_value: Optional[str] = None,
        actual_value: Optional[str] = None,
        notes: Optional[str] = None
    ) -> None:
        """Actualizar diferencia"""
        if metric is not None:
            self.metric = metric
        if planned_value is not None:
            self.planned_value = planned_value
        if actual_value is not None:
            self.actual_value = actual_value
        if notes is not None:
            self.notes = notes
        
        self.updated_at = datetime.utcnow()

    def has_significant_difference(self) -> bool:
        """Verificar si existe diferencia significativa"""
        return self.planned_value != self.actual_value

    def get_variance_percentage(self) -> Optional[float]:
        """Calcular porcentaje de variación para valores numéricos"""
        try:
            planned_num = float(self.planned_value)
            actual_num = float(self.actual_value)
            
            if planned_num == 0:
                return 100.0 if actual_num != 0 else 0.0
            
            return ((actual_num - planned_num) / planned_num) * 100
        except (ValueError, TypeError):
            return None

    def is_associated_with_day(self) -> bool:
        """Verificar si está asociada a un día específico"""
        return self.day_id is not None

    def is_associated_with_activity(self) -> bool:
        """Verificar si está asociada a una actividad específica"""
        return self.activity_id is not None

    def soft_delete(self) -> None:
        """Marcar como eliminada"""
        self.is_deleted = True
        self.updated_at = datetime.utcnow()

    def restore(self) -> None:
        """Restaurar diferencia eliminada"""
        self.is_deleted = False
        self.updated_at = datetime.utcnow()