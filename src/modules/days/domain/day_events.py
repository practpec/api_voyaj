from dataclasses import dataclass
from datetime import datetime, date
from shared.events.base_event import DomainEvent


DAY_EVENT_TYPES = {
    "DAY_CREATED": "day_created",
    "DAY_UPDATED": "day_updated",
    "DAY_DELETED": "day_deleted",
    "DAY_NOTES_UPDATED": "day_notes_updated"
}


@dataclass
class DayCreatedEvent(DomainEvent):
    trip_id: str = ""
    day_id: str = ""
    date: date = None
    created_by: str = ""
    
    def __post_init__(self):
        self.event_type = DAY_EVENT_TYPES["DAY_CREATED"]
        self.occurred_at = datetime.utcnow()


@dataclass
class DayUpdatedEvent(DomainEvent):
    trip_id: str = ""
    day_id: str = ""
    updated_by: str = ""
    updated_fields: list = None
    
    def __post_init__(self):
        self.event_type = DAY_EVENT_TYPES["DAY_UPDATED"]
        self.occurred_at = datetime.utcnow()


@dataclass
class DayDeletedEvent(DomainEvent):
    trip_id: str = ""
    day_id: str = ""
    deleted_by: str = ""
    
    def __post_init__(self):
        self.event_type = DAY_EVENT_TYPES["DAY_DELETED"]
        self.occurred_at = datetime.utcnow()


@dataclass
class DayNotesUpdatedEvent(DomainEvent):
    trip_id: str = ""
    day_id: str = ""
    updated_by: str = ""
    
    def __post_init__(self):
        self.event_type = DAY_EVENT_TYPES["DAY_NOTES_UPDATED"]
        self.occurred_at = datetime.utcnow()