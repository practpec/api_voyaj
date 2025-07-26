from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from shared.events.base_event import DomainEvent


ACTIVITY_EVENT_TYPES = {
    "ACTIVITY_CREATED": "activity_created",
    "ACTIVITY_UPDATED": "activity_updated",
    "ACTIVITY_DELETED": "activity_deleted",
    "ACTIVITY_STARTED": "activity_started",
    "ACTIVITY_COMPLETED": "activity_completed",
    "ACTIVITY_CANCELLED": "activity_cancelled",
    "ACTIVITY_ORDER_CHANGED": "activity_order_changed",
    "ACTIVITY_COST_UPDATED": "activity_cost_updated"
}


@dataclass
class ActivityCreatedEvent(DomainEvent):
    trip_id: str = ""
    day_id: str = ""
    activity_id: str = ""
    title: str = ""
    created_by: str = ""
    category: str = ""
    
    def __post_init__(self):
        self.event_type = ACTIVITY_EVENT_TYPES["ACTIVITY_CREATED"]
        self.occurred_at = datetime.utcnow()


@dataclass
class ActivityUpdatedEvent(DomainEvent):
    trip_id: str = ""
    day_id: str = ""
    activity_id: str = ""
    updated_by: str = ""
    updated_fields: list = None
    
    def __post_init__(self):
        self.event_type = ACTIVITY_EVENT_TYPES["ACTIVITY_UPDATED"]
        self.occurred_at = datetime.utcnow()


@dataclass
class ActivityDeletedEvent(DomainEvent):
    trip_id: str = ""
    day_id: str = ""
    activity_id: str = ""
    deleted_by: str = ""
    
    def __post_init__(self):
        self.event_type = ACTIVITY_EVENT_TYPES["ACTIVITY_DELETED"]
        self.occurred_at = datetime.utcnow()


@dataclass
class ActivityStartedEvent(DomainEvent):
    trip_id: str = ""
    day_id: str = ""
    activity_id: str = ""
    started_by: str = ""
    
    def __post_init__(self):
        self.event_type = ACTIVITY_EVENT_TYPES["ACTIVITY_STARTED"]
        self.occurred_at = datetime.utcnow()


@dataclass
class ActivityCompletedEvent(DomainEvent):
    trip_id: str = ""
    day_id: str = ""
    activity_id: str = ""
    completed_by: str = ""
    actual_cost: Optional[float] = None
    
    def __post_init__(self):
        self.event_type = ACTIVITY_EVENT_TYPES["ACTIVITY_COMPLETED"]
        self.occurred_at = datetime.utcnow()


@dataclass
class ActivityCancelledEvent(DomainEvent):
    trip_id: str = ""
    day_id: str = ""
    activity_id: str = ""
    cancelled_by: str = ""
    
    def __post_init__(self):
        self.event_type = ACTIVITY_EVENT_TYPES["ACTIVITY_CANCELLED"]
        self.occurred_at = datetime.utcnow()


@dataclass
class ActivityOrderChangedEvent(DomainEvent):
    trip_id: str = ""
    day_id: str = ""
    activity_id: str = ""
    old_order: int = 0
    new_order: int = 0
    changed_by: str = ""
    
    def __post_init__(self):
        self.event_type = ACTIVITY_EVENT_TYPES["ACTIVITY_ORDER_CHANGED"]
        self.occurred_at = datetime.utcnow()


@dataclass
class ActivityCostUpdatedEvent(DomainEvent):
    trip_id: str = ""
    day_id: str = ""
    activity_id: str = ""
    old_cost: Optional[float] = None
    new_cost: Optional[float] = None
    updated_by: str = ""
    
    def __post_init__(self):
        self.event_type = ACTIVITY_EVENT_TYPES["ACTIVITY_COST_UPDATED"]
        self.occurred_at = datetime.utcnow()