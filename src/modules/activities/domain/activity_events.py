# src/modules/activities/domain/activity_events.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
from shared.events.base_event import DomainEvent


@dataclass
class ActivityCreatedEvent(DomainEvent):
    activity_id: str = ""
    day_id: str = ""
    trip_id: str = ""
    created_by: str = ""
    title: str = ""
    category: str = ""
    
    def __post_init__(self):
        super().__post_init__()
        self.event_type = "activity.created"
        self.aggregate_type = "Activity"
        self.aggregate_id = self.activity_id
        self.metadata = {
            "day_id": self.day_id,
            "trip_id": self.trip_id,
            "created_by": self.created_by,
            "title": self.title,
            "category": self.category
        }


@dataclass
class ActivityUpdatedEvent(DomainEvent):
    activity_id: str = ""
    day_id: str = ""
    trip_id: str = ""
    updated_by: str = ""
    updated_fields: Optional[List[str]] = None
    
    def __post_init__(self):
        super().__post_init__()
        self.event_type = "activity.updated"
        self.aggregate_type = "Activity"
        self.aggregate_id = self.activity_id
        self.metadata = {
            "day_id": self.day_id,
            "trip_id": self.trip_id,
            "updated_by": self.updated_by,
            "updated_fields": self.updated_fields or []
        }


@dataclass
class ActivityStatusChangedEvent(DomainEvent):
    activity_id: str = ""
    day_id: str = ""
    trip_id: str = ""
    changed_by: str = ""
    old_status: str = ""
    new_status: str = ""
    
    def __post_init__(self):
        super().__post_init__()
        self.event_type = "activity.status_changed"
        self.aggregate_type = "Activity"
        self.aggregate_id = self.activity_id
        self.metadata = {
            "day_id": self.day_id,
            "trip_id": self.trip_id,
            "changed_by": self.changed_by,
            "old_status": self.old_status,
            "new_status": self.new_status
        }


@dataclass
class ActivityCompletedEvent(DomainEvent):
    activity_id: str = ""
    day_id: str = ""
    trip_id: str = ""
    completed_by: str = ""
    actual_duration: Optional[int] = None
    actual_cost: Optional[float] = None
    
    def __post_init__(self):
        super().__post_init__()
        self.event_type = "activity.completed"
        self.aggregate_type = "Activity"
        self.aggregate_id = self.activity_id
        self.metadata = {
            "day_id": self.day_id,
            "trip_id": self.trip_id,
            "completed_by": self.completed_by,
            "actual_duration": self.actual_duration,
            "actual_cost": self.actual_cost
        }


@dataclass
class ActivitiesReorderedEvent(DomainEvent):
    day_id: str = ""
    trip_id: str = ""
    reordered_by: str = ""
    activity_orders: Optional[List[Dict[str, Any]]] = None
    
    def __post_init__(self):
        super().__post_init__()
        self.event_type = "activities.reordered"
        self.aggregate_type = "Day"
        self.aggregate_id = self.day_id
        self.metadata = {
            "trip_id": self.trip_id,
            "reordered_by": self.reordered_by,
            "activity_orders": self.activity_orders or []
        }


@dataclass
class ActivityDeletedEvent(DomainEvent):
    activity_id: str = ""
    day_id: str = ""
    trip_id: str = ""
    deleted_by: str = ""
    title: str = ""
    
    def __post_init__(self):
        super().__post_init__()
        self.event_type = "activity.deleted"
        self.aggregate_type = "Activity"
        self.aggregate_id = self.activity_id
        self.metadata = {
            "day_id": self.day_id,
            "trip_id": self.trip_id,
            "deleted_by": self.deleted_by,
            "title": self.title
        }