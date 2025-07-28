# src/shared/events/base_event.py
from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional, Dict


@dataclass
class BaseEvent(ABC):
    """Clase base simple para eventos"""
    event_type: str
    occurred_at: datetime
    
    def __init__(self):
        self.occurred_at = datetime.utcnow()
        self.event_type = ""


@dataclass
class DomainEvent(ABC):
    """Clase base para todos los eventos de dominio"""
    event_type: str = ""
    occurred_at: datetime = None
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


class BaseEventHandler(ABC):
    """Clase base para manejadores de eventos"""
    
    async def _send_notification(self, notification_data: Dict[str, Any]) -> None:
        """Enviar notificación a usuarios relevantes"""
        try:
            print(f"[NOTIFICATION] {notification_data}")
        except Exception as e:
            print(f"[ERROR] Error enviando notificación: {str(e)}")