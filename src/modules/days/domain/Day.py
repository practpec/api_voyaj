from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional
from uuid import uuid4


@dataclass
class DayData:
    id: str
    trip_id: str
    date: date
    notes: Optional[str]
    is_deleted: bool = False
    created_at: datetime = None
    updated_at: datetime = None


class Day:
    def __init__(
        self,
        id: str,
        trip_id: str,
        date: date,
        notes: Optional[str] = None,
        is_deleted: bool = False,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self._id = id
        self._trip_id = trip_id
        self._date = date
        self._notes = notes
        self._is_deleted = is_deleted
        self._created_at = created_at or datetime.utcnow()
        self._updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(cls, trip_id: str, date: date, notes: Optional[str] = None) -> 'Day':
        """Crear nuevo día para un viaje"""
        return cls(
            id=str(uuid4()),
            trip_id=trip_id,
            date=date,
            notes=notes,
            is_deleted=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    @classmethod
    def from_data(cls, data: DayData) -> 'Day':
        """Crear instancia desde datos"""
        return cls(
            id=data.id,
            trip_id=data.trip_id,
            date=data.date,
            notes=data.notes,
            is_deleted=data.is_deleted,
            created_at=data.created_at,
            updated_at=data.updated_at
        )

    def update_notes(self, notes: Optional[str]) -> None:
        """Actualizar notas del día"""
        self._notes = notes
        self._updated_at = datetime.utcnow()

    def soft_delete(self) -> None:
        """Eliminar día (soft delete)"""
        self._is_deleted = True
        self._updated_at = datetime.utcnow()

    def restore(self) -> None:
        """Restaurar día eliminado"""
        self._is_deleted = False
        self._updated_at = datetime.utcnow()

    def is_active(self) -> bool:
        """Verificar si el día está activo"""
        return not self._is_deleted

    def to_public_data(self) -> DayData:
        """Convertir a datos públicos"""
        return DayData(
            id=self._id,
            trip_id=self._trip_id,
            date=self._date,
            notes=self._notes,
            is_deleted=self._is_deleted,
            created_at=self._created_at,
            updated_at=self._updated_at
        )

    @property
    def id(self) -> str:
        return self._id

    @property
    def trip_id(self) -> str:
        return self._trip_id

    @property
    def date(self) -> date:
        return self._date

    @property
    def notes(self) -> Optional[str]:
        return self._notes

    @property
    def is_deleted(self) -> bool:
        return self._is_deleted