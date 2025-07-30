# src/modules/activities/domain/Activity.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import uuid4


@dataclass
class ActivityData:
    id: str
    day_id: str
    trip_id: str
    title: str
    description: Optional[str]
    category: str
    status: str
    priority: str
    order: int
    estimated_duration: Optional[int]
    actual_duration: Optional[int]
    estimated_cost: Optional[float]
    actual_cost: Optional[float]
    currency: str
    location: Optional[str]
    coordinates: Optional[Dict[str, float]]
    notes: Optional[str]
    tags: List[str]
    external_links: List[str]
    booking_info: Optional[Dict[str, Any]]
    rating: Optional[int]
    review: Optional[str]
    created_by: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    deleted_at: Optional[datetime]


class Activity:
    def __init__(self, data: ActivityData):
        self._data = data

    @classmethod
    def create(
        cls,
        day_id: str,
        trip_id: str,
        title: str,
        created_by: str,
        description: Optional[str] = None,
        category: str = "general",
        estimated_duration: Optional[int] = None,
        estimated_cost: Optional[float] = None,
        currency: str = "USD",
        location: Optional[str] = None,
        coordinates: Optional[Dict[str, float]] = None,
        notes: Optional[str] = None,
        priority: str = "medium",
        tags: Optional[List[str]] = None,
        external_links: Optional[List[str]] = None,
        booking_info: Optional[Dict[str, Any]] = None,
        order: int = 0
    ):
        """Crear nueva actividad"""
        now = datetime.utcnow()
        
        data = ActivityData(
            id=str(uuid4()),
            day_id=day_id,
            trip_id=trip_id,
            title=title,
            description=description,
            category=category,
            status="pending",
            priority=priority,
            order=order,
            estimated_duration=estimated_duration,
            actual_duration=None,
            estimated_cost=estimated_cost,
            actual_cost=None,
            currency=currency,
            location=location,
            coordinates=coordinates,
            notes=notes,
            tags=tags or [],
            external_links=external_links or [],
            booking_info=booking_info,
            rating=None,
            review=None,
            created_by=created_by,
            created_at=now,
            updated_at=now,
            completed_at=None,
            deleted_at=None
        )
        
        return cls(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Crear instancia desde diccionario"""
        activity_data = ActivityData(
            id=data.get("id"),
            day_id=data.get("day_id"),
            trip_id=data.get("trip_id"),
            title=data.get("title"),
            description=data.get("description"),
            category=data.get("category"),
            status=data.get("status"),
            priority=data.get("priority"),
            order=data.get("order", 0),
            estimated_duration=data.get("estimated_duration"),
            actual_duration=data.get("actual_duration"),
            estimated_cost=data.get("estimated_cost"),
            actual_cost=data.get("actual_cost"),
            currency=data.get("currency", "USD"),
            location=data.get("location"),
            coordinates=data.get("coordinates"),
            notes=data.get("notes"),
            tags=data.get("tags", []),
            external_links=data.get("external_links", []),
            booking_info=data.get("booking_info"),
            rating=data.get("rating"),
            review=data.get("review"),
            created_by=data.get("created_by"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            completed_at=data.get("completed_at"),
            deleted_at=data.get("deleted_at")
        )
        
        return cls(activity_data)

    # Propiedades de acceso
    @property
    def id(self) -> str:
        return self._data.id

    @property
    def day_id(self) -> str:
        return self._data.day_id

    @property
    def trip_id(self) -> str:
        return self._data.trip_id

    @property
    def title(self) -> str:
        return self._data.title

    @property
    def status(self) -> str:
        return self._data.status

    @property
    def priority(self) -> str:
        return self._data.priority

    @property
    def order(self) -> int:
        return self._data.order

    @property
    def created_by(self) -> str:
        return self._data.created_by

    @property
    def actual_duration(self) -> Optional[int]:
        return self._data.actual_duration

    @property
    def actual_cost(self) -> Optional[float]:
        return self._data.actual_cost

    @property
    def created_at(self) -> datetime:
        return self._data.created_at

    # Métodos de negocio
    def update_details(self, **kwargs):
        """Actualizar detalles de la actividad"""
        for key, value in kwargs.items():
            if hasattr(self._data, key):
                setattr(self._data, key, value)
        
        self._data.updated_at = datetime.utcnow()

    def change_status(
        self, 
        new_status: str, 
        notes: Optional[str] = None,
        actual_start_time: Optional[datetime] = None,
        actual_end_time: Optional[datetime] = None,
        actual_cost: Optional[float] = None
    ):
        """Cambiar estado de la actividad"""
        self._data.status = new_status
        
        if notes:
            self._data.notes = notes
            
        if actual_cost is not None:
            self._data.actual_cost = actual_cost
            
        if new_status == "completed":
            self._data.completed_at = datetime.utcnow()
            
            # Calcular duración real si se proporcionan las horas
            if actual_start_time and actual_end_time:
                duration_minutes = int((actual_end_time - actual_start_time).total_seconds() / 60)
                self._data.actual_duration = duration_minutes
        
        self._data.updated_at = datetime.utcnow()

    def update_order(self, new_order: int):
        """Actualizar orden de la actividad"""
        self._data.order = new_order
        self._data.updated_at = datetime.utcnow()

    def soft_delete(self):
        """Eliminación lógica"""
        self._data.deleted_at = datetime.utcnow()
        self._data.updated_at = datetime.utcnow()

    def is_active(self) -> bool:
        """Verificar si la actividad está activa"""
        return self._data.deleted_at is None

    def is_completed(self) -> bool:
        """Verificar si la actividad está completada"""
        return self._data.status == "completed"

    def can_be_edited(self) -> bool:
        """Verificar si la actividad puede ser editada"""
        return self.is_active() and self._data.status not in ["completed", "cancelled"]

    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para persistencia"""
        return {
            "id": self._data.id,
            "day_id": self._data.day_id,
            "trip_id": self._data.trip_id,
            "title": self._data.title,
            "description": self._data.description,
            "category": self._data.category,
            "status": self._data.status,
            "priority": self._data.priority,
            "order": self._data.order,
            "estimated_duration": self._data.estimated_duration,
            "actual_duration": self._data.actual_duration,
            "estimated_cost": self._data.estimated_cost,
            "actual_cost": self._data.actual_cost,
            "currency": self._data.currency,
            "location": self._data.location,
            "coordinates": self._data.coordinates,
            "notes": self._data.notes,
            "tags": self._data.tags,
            "external_links": self._data.external_links,
            "booking_info": self._data.booking_info,
            "rating": self._data.rating,
            "review": self._data.review,
            "created_by": self._data.created_by,
            "created_at": self._data.created_at,
            "updated_at": self._data.updated_at,
            "completed_at": self._data.completed_at,
            "deleted_at": self._data.deleted_at
        }

    def to_public_data(self) -> Dict[str, Any]:
        """Convertir a diccionario para respuestas públicas"""
        return {
            "id": self._data.id,
            "day_id": self._data.day_id,
            "trip_id": self._data.trip_id,
            "title": self._data.title,
            "description": self._data.description,
            "category": self._data.category,
            "status": self._data.status,
            "priority": self._data.priority,
            "order": self._data.order,
            "estimated_duration": self._data.estimated_duration,
            "actual_duration": self._data.actual_duration,
            "estimated_cost": self._data.estimated_cost,
            "actual_cost": self._data.actual_cost,
            "currency": self._data.currency,
            "location": self._data.location,
            "coordinates": self._data.coordinates,
            "notes": self._data.notes,
            "tags": self._data.tags,
            "external_links": self._data.external_links,
            "booking_info": self._data.booking_info,
            "rating": self._data.rating,
            "review": self._data.review,
            "created_by": self._data.created_by,
            "created_at": self._data.created_at,
            "updated_at": self._data.updated_at,
            "completed_at": self._data.completed_at
        }