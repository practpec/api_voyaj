# src/modules/activities/domain/activity_events.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
from shared.events.base_event import BaseEvent


@dataclass
class ActivityCreatedEvent(BaseEvent):
    activity_id: str
    day_id: str
    trip_id: str
    created_by: str
    title: str
    category: str
    
    def __post_init__(self):
        super().__init__(
            event_type="activity.created",
            aggregate_id=self.activity_id,
            occurred_at=datetime.utcnow(),
            metadata={
                "day_id": self.day_id,
                "trip_id": self.trip_id,
                "created_by": self.created_by,
                "title": self.title,
                "category": self.category
            }
        )


@dataclass
class ActivityUpdatedEvent(BaseEvent):
    activity_id: str
    day_id: str
    trip_id: str
    updated_by: str
    updated_fields: List[str]
    
    def __post_init__(self):
        super().__init__(
            event_type="activity.updated",
            aggregate_id=self.activity_id,
            occurred_at=datetime.utcnow(),
            metadata={
                "day_id": self.day_id,
                "trip_id": self.trip_id,
                "updated_by": self.updated_by,
                "updated_fields": self.updated_fields
            }
        )


@dataclass
class ActivityStatusChangedEvent(BaseEvent):
    activity_id: str
    day_id: str
    trip_id: str
    changed_by: str
    old_status: str
    new_status: str
    
    def __post_init__(self):
        super().__init__(
            event_type="activity.status_changed",
            aggregate_id=self.activity_id,
            occurred_at=datetime.utcnow(),
            metadata={
                "day_id": self.day_id,
                "trip_id": self.trip_id,
                "changed_by": self.changed_by,
                "old_status": self.old_status,
                "new_status": self.new_status
            }
        )


@dataclass
class ActivityCompletedEvent(BaseEvent):
    activity_id: str
    day_id: str
    trip_id: str
    completed_by: str
    actual_duration: Optional[int] = None
    actual_cost: Optional[float] = None
    
    def __post_init__(self):
        super().__init__(
            event_type="activity.completed",
            aggregate_id=self.activity_id,
            occurred_at=datetime.utcnow(),
            metadata={
                "day_id": self.day_id,
                "trip_id": self.trip_id,
                "completed_by": self.completed_by,
                "actual_duration": self.actual_duration,
                "actual_cost": self.actual_cost
            }
        )


@dataclass
class ActivitiesReorderedEvent(BaseEvent):
    day_id: str
    trip_id: str
    reordered_by: str
    activity_orders: List[Dict[str, Any]]
    
    def __post_init__(self):
        super().__init__(
            event_type="activities.reordered",
            aggregate_id=self.day_id,
            occurred_at=datetime.utcnow(),
            metadata={
                "trip_id": self.trip_id,
                "reordered_by": self.reordered_by,
                "activity_orders": self.activity_orders
            }
        )


@dataclass
class ActivityDeletedEvent(BaseEvent):
    activity_id: str
    day_id: str
    trip_id: str
    deleted_by: str
    title: str
    
    def __post_init__(self):
        super().__init__(
            event_type="activity.deleted",
            aggregate_id=self.activity_id,
            occurred_at=datetime.utcnow(),
            metadata={
                "day_id": self.day_id,
                "trip_id": self.trip_id,
                "deleted_by": self.deleted_by,
                "title": self.title
            }
        )