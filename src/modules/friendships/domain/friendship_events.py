from dataclasses import dataclass
from datetime import datetime
from shared.events.base_event import DomainEvent


@dataclass
class FriendRequestSentEvent(DomainEvent):
    requester_id: str = ""
    recipient_id: str = ""
    friendship_id: str = ""
    
    def __post_init__(self):
        self.event_type = "friend_request_sent"
        self.occurred_at = datetime.utcnow()


@dataclass
class FriendRequestAcceptedEvent(DomainEvent):
    requester_id: str = ""
    recipient_id: str = ""
    friendship_id: str = ""
    
    def __post_init__(self):
        self.event_type = "friend_request_accepted"
        self.occurred_at = datetime.utcnow()


@dataclass
class FriendRequestRejectedEvent(DomainEvent):
    requester_id: str = ""
    recipient_id: str = ""
    friendship_id: str = ""
    
    def __post_init__(self):
        self.event_type = "friend_request_rejected"
        self.occurred_at = datetime.utcnow()


@dataclass
class FriendshipRemovedEvent(DomainEvent):
    user_id: str = ""
    friend_id: str = ""
    friendship_id: str = ""
    
    def __post_init__(self):
        self.event_type = "friendship_removed"
        self.occurred_at = datetime.utcnow()