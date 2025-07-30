from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from shared.events.base_event import DomainEvent


DIARY_ENTRY_EVENT_TYPES = {
    "DIARY_ENTRY_CREATED": "diary_entry_created",
    "DIARY_ENTRY_UPDATED": "diary_entry_updated",
    "DIARY_ENTRY_DELETED": "diary_entry_deleted",
    "DIARY_ENTRY_EMOTIONS_UPDATED": "diary_entry_emotions_updated",
    "DIARY_ENTRY_RESTORED": "diary_entry_restored"
}


@dataclass
class DiaryEntryCreatedEvent(DomainEvent):
    trip_id: str = ""
    day_id: str = ""
    entry_id: str = ""
    user_id: str = ""
    word_count: int = 0
    has_emotions: bool = False
    
    def __post_init__(self):
        self.event_type = DIARY_ENTRY_EVENT_TYPES["DIARY_ENTRY_CREATED"]
        self.occurred_at = datetime.utcnow()


@dataclass
class DiaryEntryUpdatedEvent(DomainEvent):
    trip_id: str = ""
    day_id: str = ""
    entry_id: str = ""
    user_id: str = ""
    updated_fields: List[str] = None
    old_word_count: int = 0
    new_word_count: int = 0
    
    def __post_init__(self):
        self.event_type = DIARY_ENTRY_EVENT_TYPES["DIARY_ENTRY_UPDATED"]
        self.occurred_at = datetime.utcnow()


@dataclass
class DiaryEntryDeletedEvent(DomainEvent):
    trip_id: str = ""
    day_id: str = ""
    entry_id: str = ""
    user_id: str = ""
    deleted_by: str = ""
    
    def __post_init__(self):
        self.event_type = DIARY_ENTRY_EVENT_TYPES["DIARY_ENTRY_DELETED"]
        self.occurred_at = datetime.utcnow()


@dataclass
class DiaryEntryEmotionsUpdatedEvent(DomainEvent):
    trip_id: str = ""
    day_id: str = ""
    entry_id: str = ""
    user_id: str = ""
    dominant_emotion: Optional[str] = None
    emotions_count: int = 0
    
    def __post_init__(self):
        self.event_type = DIARY_ENTRY_EVENT_TYPES["DIARY_ENTRY_EMOTIONS_UPDATED"]
        self.occurred_at = datetime.utcnow()


@dataclass
class DiaryEntryRestoredEvent(DomainEvent):
    trip_id: str = ""
    day_id: str = ""
    entry_id: str = ""
    user_id: str = ""
    restored_by: str = ""
    
    def __post_init__(self):
        self.event_type = DIARY_ENTRY_EVENT_TYPES["DIARY_ENTRY_RESTORED"]
        self.occurred_at = datetime.utcnow()