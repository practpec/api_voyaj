# src/modules/days/domain/day_events.py
from dataclasses import dataclass
from datetime import datetime
from datetime import date as DateType  # Alias para evitar conflicto
from typing import List, Optional, Dict, Any
from shared.events.base_event import DomainEvent


@dataclass
class DayCreatedEvent(DomainEvent):
    """Evento emitido cuando se crea un día"""
    trip_id: str = ""
    day_id: str = ""
    date: Optional[DateType] = None
    created_by: str = ""

    def __post_init__(self):
        super().__post_init__()
        self.event_type = "day.created"
        self.aggregate_type = 'Day'
        self.aggregate_id = self.day_id


@dataclass
class DayUpdatedEvent(DomainEvent):
    """Evento emitido cuando se actualiza un día"""
    trip_id: str = ""
    day_id: str = ""
    updated_by: str = ""
    updated_fields: Optional[List[str]] = None

    def __post_init__(self):
        super().__post_init__()
        self.event_type = "day.updated"
        self.aggregate_type = 'Day'
        self.aggregate_id = self.day_id
        if self.updated_fields is None:
            self.updated_fields = []


@dataclass
class DayDeletedEvent(DomainEvent):
    """Evento emitido cuando se elimina un día"""
    trip_id: str = ""
    day_id: str = ""
    deleted_by: str = ""

    def __post_init__(self):
        super().__post_init__()
        self.event_type = "day.deleted"
        self.aggregate_type = 'Day'
        self.aggregate_id = self.day_id


@dataclass
class DayNotesUpdatedEvent(DomainEvent):
    """Evento emitido cuando se actualizan las notas de un día"""
    trip_id: str = ""
    day_id: str = ""
    updated_by: str = ""

    def __post_init__(self):
        super().__post_init__()
        self.event_type = "day.notes_updated"
        self.aggregate_type = 'Day'
        self.aggregate_id = self.day_id


@dataclass
class BulkDaysCreatedEvent(DomainEvent):
    """Evento emitido cuando se crean múltiples días en lote"""
    trip_id: str = ""
    created_by: str = ""
    total_created: int = 0
    day_ids: Optional[List[str]] = None

    def __post_init__(self):
        super().__post_init__()
        self.event_type = "days.bulk_created"
        self.aggregate_type = 'Trip'
        self.aggregate_id = self.trip_id
        if self.day_ids is None:
            self.day_ids = []


@dataclass
class TripDaysGeneratedEvent(DomainEvent):
    """Evento emitido cuando se generan automáticamente los días de un viaje"""
    trip_id: str = ""
    generated_by: str = ""
    generated_days: int = 0

    def __post_init__(self):
        super().__post_init__()
        self.event_type = "trip.days_generated"
        self.aggregate_type = 'Trip'
        self.aggregate_id = self.trip_id