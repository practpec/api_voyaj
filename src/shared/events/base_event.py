from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional, Dict


@dataclass
class DomainEvent(ABC):
    """Clase base para todos los eventos de dominio"""
    event_type: str
    occurred_at: datetime
    aggregate_id: Optional[str] = None
    aggregate_type: Optional[str] = None
    event_data: Optional[Any] = None
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.occurred_at is None:
            self.occurred_at = datetime.utcnow()


@dataclass
class UserEvent(DomainEvent):
    """Evento específico para usuarios"""
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_type = 'User'


@dataclass
class TripEvent(DomainEvent):
    """Evento específico para viajes"""
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_type = 'Trip'


@dataclass
class FriendshipEvent(DomainEvent):
    """Evento específico para amistades"""
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_type = 'Friendship'