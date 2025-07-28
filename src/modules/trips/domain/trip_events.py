from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from shared.events.base_event import DomainEvent


TRIP_EVENT_TYPES = {
    "TRIP_CREATED": "trip_created",
    "TRIP_UPDATED": "trip_updated", 
    "TRIP_DELETED": "trip_deleted",
    "TRIP_STATUS_CHANGED": "trip_status_changed",
    "TRIP_COMPLETED": "trip_completed",
    "TRIP_CANCELLED": "trip_cancelled",
    "MEMBER_INVITED": "member_invited",
    "MEMBER_JOINED": "member_joined",
    "MEMBER_LEFT": "member_left",
    "MEMBER_REMOVED": "member_removed",
    "MEMBER_ROLE_CHANGED": "member_role_changed",
    "INVITATION_SENT": "invitation_sent",
    "INVITATION_ACCEPTED": "invitation_accepted",
    "INVITATION_REJECTED": "invitation_rejected",
    "INVITATION_CANCELLED": "invitation_cancelled"
}


@dataclass
class TripCreatedEvent(DomainEvent):
    trip_id: str = ""
    owner_id: str = ""
    title: str = ""
    destination: str = ""
    
    def __post_init__(self):
        self.event_type = TRIP_EVENT_TYPES["TRIP_CREATED"]
        self.occurred_at = datetime.utcnow()


@dataclass
class TripUpdatedEvent(DomainEvent):
    trip_id: str = ""
    owner_id: str = ""
    updated_by: str = ""  # Agregar este campo
    updated_fields: Optional[list] = None  # Cambiar a list en lugar de dict
    
    def __post_init__(self):
        self.event_type = TRIP_EVENT_TYPES["TRIP_UPDATED"]
        self.occurred_at = datetime.utcnow()

@dataclass
class TripDeletedEvent(DomainEvent):
    trip_id: str = ""
    owner_id: str = ""
    
    def __post_init__(self):
        self.event_type = TRIP_EVENT_TYPES["TRIP_DELETED"]
        self.occurred_at = datetime.utcnow()


@dataclass
class TripStatusChangedEvent(DomainEvent):
    trip_id: str = ""
    owner_id: str = ""
    old_status: str = ""
    new_status: str = ""
    
    def __post_init__(self):
        self.event_type = TRIP_EVENT_TYPES["TRIP_STATUS_CHANGED"]
        self.occurred_at = datetime.utcnow()


@dataclass
class TripCompletedEvent(DomainEvent):
    trip_id: str = ""
    owner_id: str = ""
    
    def __post_init__(self):
        self.event_type = TRIP_EVENT_TYPES["TRIP_COMPLETED"]
        self.occurred_at = datetime.utcnow()


@dataclass
class TripCancelledEvent(DomainEvent):
    trip_id: str = ""
    owner_id: str = ""
    
    def __post_init__(self):
        self.event_type = TRIP_EVENT_TYPES["TRIP_CANCELLED"]
        self.occurred_at = datetime.utcnow()


@dataclass
class MemberInvitedEvent(DomainEvent):
    trip_id: str = ""
    invited_user_id: str = ""
    invited_by: str = ""
    role: str = ""
    
    def __post_init__(self):
        self.event_type = TRIP_EVENT_TYPES["MEMBER_INVITED"]
        self.occurred_at = datetime.utcnow()


@dataclass
class MemberJoinedEvent(DomainEvent):
    trip_id: str = ""
    user_id: str = ""
    role: str = ""
    
    def __post_init__(self):
        self.event_type = TRIP_EVENT_TYPES["MEMBER_JOINED"]
        self.occurred_at = datetime.utcnow()


@dataclass
class MemberLeftEvent(DomainEvent):
    trip_id: str = ""
    user_id: str = ""
    
    def __post_init__(self):
        self.event_type = TRIP_EVENT_TYPES["MEMBER_LEFT"]
        self.occurred_at = datetime.utcnow()


@dataclass
class MemberRemovedEvent(DomainEvent):
    trip_id: str = ""
    removed_user_id: str = ""
    removed_by: str = ""
    
    def __post_init__(self):
        self.event_type = TRIP_EVENT_TYPES["MEMBER_REMOVED"]
        self.occurred_at = datetime.utcnow()


@dataclass
class MemberRoleChangedEvent(DomainEvent):
    trip_id: str = ""
    user_id: str = ""
    old_role: str = ""
    new_role: str = ""
    changed_by: str = ""
    
    def __post_init__(self):
        self.event_type = TRIP_EVENT_TYPES["MEMBER_ROLE_CHANGED"]
        self.occurred_at = datetime.utcnow()


@dataclass
class InvitationSentEvent(DomainEvent):
    trip_id: str = ""
    invited_user_id: str = ""
    invited_by: str = ""
    
    def __post_init__(self):
        self.event_type = TRIP_EVENT_TYPES["INVITATION_SENT"]
        self.occurred_at = datetime.utcnow()


@dataclass
class InvitationAcceptedEvent(DomainEvent):
    trip_id: str = ""
    user_id: str = ""
    invitation_id: str = ""
    
    def __post_init__(self):
        self.event_type = TRIP_EVENT_TYPES["INVITATION_ACCEPTED"]
        self.occurred_at = datetime.utcnow()


@dataclass
class InvitationRejectedEvent(DomainEvent):
    trip_id: str = ""
    user_id: str = ""
    invitation_id: str = ""
    
    def __post_init__(self):
        self.event_type = TRIP_EVENT_TYPES["INVITATION_REJECTED"]
        self.occurred_at = datetime.utcnow()


@dataclass
class InvitationCancelledEvent(DomainEvent):
    trip_id: str = ""
    cancelled_user_id: str = ""
    cancelled_by: str = ""
    invitation_id: str = ""
    
    def __post_init__(self):
        self.event_type = TRIP_EVENT_TYPES["INVITATION_CANCELLED"]
        self.occurred_at = datetime.utcnow()