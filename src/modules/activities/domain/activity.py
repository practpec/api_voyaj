from dataclasses import dataclass
from datetime import datetime, time
from typing import Optional
from uuid import uuid4
from enum import Enum


class ActivityStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ActivityCategory(str, Enum):
    TRANSPORT = "transport"
    ACCOMMODATION = "accommodation"
    FOOD = "food"
    SIGHTSEEING = "sightseeing"
    ENTERTAINMENT = "entertainment"
    SHOPPING = "shopping"
    ADVENTURE = "adventure"
    RELAXATION = "relaxation"
    CULTURAL = "cultural"
    BUSINESS = "business"
    OTHER = "other"


@dataclass
class ActivityData:
    id: str
    day_id: str
    title: str
    description: Optional[str]
    location: Optional[str]
    start_time: Optional[time]
    end_time: Optional[time]
    estimated_cost: Optional[float]
    actual_cost: Optional[float]
    category: str
    status: str
    order: int
    created_by: str
    is_deleted: bool = False
    created_at: datetime = None
    updated_at: datetime = None


class Activity:
    def __init__(
        self,
        id: str,
        day_id: str,
        title: str,
        description: Optional[str],
        location: Optional[str],
        start_time: Optional[time],
        end_time: Optional[time],
        estimated_cost: Optional[float],
        actual_cost: Optional[float],
        category: str,
        status: str,
        order: int,
        created_by: str,
        is_deleted: bool = False,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self._id = id
        self._day_id = day_id
        self._title = title
        self._description = description
        self._location = location
        self._start_time = start_time
        self._end_time = end_time
        self._estimated_cost = estimated_cost
        self._actual_cost = actual_cost
        self._category = category
        self._status = status
        self._order = order
        self._created_by = created_by
        self._is_deleted = is_deleted
        self._created_at = created_at
        self._updated_at = updated_at

    @classmethod
    def create(
        cls,
        day_id: str,
        title: str,
        created_by: str,
        description: Optional[str] = None,
        location: Optional[str] = None,
        start_time: Optional[time] = None,
        end_time: Optional[time] = None,
        estimated_cost: Optional[float] = None,
        category: ActivityCategory = ActivityCategory.OTHER,
        order: int = 0
    ) -> 'Activity':
        """Crear nueva actividad"""
        if start_time and end_time and start_time >= end_time:
            raise ValueError("La hora de inicio debe ser anterior a la hora de fin")
        
        return cls(
            id=str(uuid4()),
            day_id=day_id,
            title=title,
            description=description,
            location=location,
            start_time=start_time,
            end_time=end_time,
            estimated_cost=estimated_cost,
            actual_cost=None,
            category=category.value,
            status=ActivityStatus.PLANNED.value,
            order=order,
            created_by=created_by,
            is_deleted=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    @classmethod
    def from_data(cls, data: ActivityData) -> 'Activity':
        """Crear instancia desde datos"""
        return cls(
            id=data.id,
            day_id=data.day_id,
            title=data.title,
            description=data.description,
            location=data.location,
            start_time=data.start_time,
            end_time=data.end_time,
            estimated_cost=data.estimated_cost,
            actual_cost=data.actual_cost,
            category=data.category,
            status=data.status,
            order=data.order,
            created_by=data.created_by,
            is_deleted=data.is_deleted,
            created_at=data.created_at,
            updated_at=data.updated_at
        )

    def update_details(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        start_time: Optional[time] = None,
        end_time: Optional[time] = None,
        estimated_cost: Optional[float] = None,
        category: Optional[ActivityCategory] = None
    ) -> None:
        """Actualizar detalles de la actividad"""
        if title is not None:
            self._title = title
        if description is not None:
            self._description = description
        if location is not None:
            self._location = location
        if start_time is not None:
            self._start_time = start_time
        if end_time is not None:
            self._end_time = end_time
        if estimated_cost is not None:
            self._estimated_cost = estimated_cost
        if category is not None:
            self._category = category.value
        
        if self._start_time and self._end_time and self._start_time >= self._end_time:
            raise ValueError("La hora de inicio debe ser anterior a la hora de fin")
        
        self._updated_at = datetime.utcnow()

    def change_status(self, new_status: ActivityStatus) -> None:
        """Cambiar estado de la actividad"""
        self._status = new_status.value
        self._updated_at = datetime.utcnow()

    def start_activity(self) -> None:
        """Marcar actividad como en progreso"""
        if self._status != ActivityStatus.PLANNED.value:
            raise ValueError("Solo se pueden iniciar actividades planificadas")
        self._status = ActivityStatus.IN_PROGRESS.value
        self._updated_at = datetime.utcnow()

    def complete_activity(self, actual_cost: Optional[float] = None) -> None:
        """Completar actividad"""
        if self._status == ActivityStatus.COMPLETED.value:
            raise ValueError("La actividad ya está completada")
        if self._status == ActivityStatus.CANCELLED.value:
            raise ValueError("No se puede completar una actividad cancelada")
        
        self._status = ActivityStatus.COMPLETED.value
        if actual_cost is not None:
            self._actual_cost = actual_cost
        self._updated_at = datetime.utcnow()

    def cancel_activity(self) -> None:
        """Cancelar actividad"""
        if self._status == ActivityStatus.COMPLETED.value:
            raise ValueError("No se puede cancelar una actividad completada")
        
        self._status = ActivityStatus.CANCELLED.value
        self._updated_at = datetime.utcnow()

    def update_order(self, new_order: int) -> None:
        """Actualizar orden de la actividad"""
        self._order = new_order
        self._updated_at = datetime.utcnow()

    def update_actual_cost(self, actual_cost: float) -> None:
        """Actualizar costo real"""
        self._actual_cost = actual_cost
        self._updated_at = datetime.utcnow()

    def soft_delete(self) -> None:
        """Eliminar actividad (soft delete)"""
        self._is_deleted = True
        self._updated_at = datetime.utcnow()

    def restore(self) -> None:
        """Restaurar actividad eliminada"""
        self._is_deleted = False
        self._updated_at = datetime.utcnow()

    def is_active(self) -> bool:
        """Verificar si la actividad está activa"""
        return not self._is_deleted

    def is_completed(self) -> bool:
        """Verificar si la actividad está completada"""
        return self._status == ActivityStatus.COMPLETED.value

    def is_in_progress(self) -> bool:
        """Verificar si la actividad está en progreso"""
        return self._status == ActivityStatus.IN_PROGRESS.value

    def is_planned(self) -> bool:
        """Verificar si la actividad está planificada"""
        return self._status == ActivityStatus.PLANNED.value

    def get_duration_minutes(self) -> Optional[int]:
        """Obtener duración en minutos"""
        if not self._start_time or not self._end_time:
            return None
        
        start_minutes = self._start_time.hour * 60 + self._start_time.minute
        end_minutes = self._end_time.hour * 60 + self._end_time.minute
        
        return end_minutes - start_minutes if end_minutes > start_minutes else None

    def to_public_data(self) -> ActivityData:
        """Convertir a datos públicos"""
        return ActivityData(
            id=self._id,
            day_id=self._day_id,
            title=self._title,
            description=self._description,
            location=self._location,
            start_time=self._start_time,
            end_time=self._end_time,
            estimated_cost=self._estimated_cost,
            actual_cost=self._actual_cost,
            category=self._category,
            status=self._status,
            order=self._order,
            created_by=self._created_by,
            is_deleted=self._is_deleted,
            created_at=self._created_at,
            updated_at=self._updated_at
        )

    @property
    def id(self) -> str:
        return self._id

    @property
    def day_id(self) -> str:
        return self._day_id

    @property
    def title(self) -> str:
        return self._title

    @property
    def status(self) -> str:
        return self._status

    @property
    def order(self) -> int:
        return self._order

    @property
    def created_by(self) -> str:
        return self._created_by