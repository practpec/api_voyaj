
import asyncio
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DomainEvent:
    event_type: str
    aggregate_id: str
    aggregate_type: str
    event_data: Any
    timestamp: datetime
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


EventHandler = Callable[[DomainEvent], None]


class EventBus:
    _instance: Optional['EventBus'] = None
    
    def __init__(self):
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._max_listeners = 100

    @classmethod
    def get_instance(cls) -> 'EventBus':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def publish(self, event: DomainEvent) -> None:
        """Publicar un evento"""
        try:
            # Obtener handlers para este tipo de evento
            handlers = self._handlers.get(event.event_type, [])
            
            # También obtener handlers globales (*)
            global_handlers = self._handlers.get('*', [])
            
            all_handlers = handlers + global_handlers
            
            if not all_handlers:
                return

            # Ejecutar todos los handlers
            for handler in all_handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    print(f"Error en handler para evento {event.event_type}: {e}")

        except Exception as e:
            print(f"Error publicando evento: {e}")
            raise e

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Suscribirse a un tipo de evento"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        
        if len(self._handlers[event_type]) >= self._max_listeners:
            raise ValueError(f"Máximo número de listeners alcanzado para {event_type}")
        
        self._handlers[event_type].append(handler)

    def subscribe_to_all(self, handler: EventHandler) -> None:
        """Suscribirse a todos los eventos"""
        self.subscribe('*', handler)

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """Desuscribirse de un evento"""
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
                if not self._handlers[event_type]:
                    del self._handlers[event_type]
            except ValueError:
                pass

    def get_listener_count(self, event_type: str) -> int:
        """Obtener número de listeners para un evento"""
        return len(self._handlers.get(event_type, []))

    def get_registered_events(self) -> List[str]:
        """Obtener todos los tipos de eventos registrados"""
        return list(self._handlers.keys())

    def remove_all_listeners(self) -> None:
        """Limpiar todos los listeners"""
        self._handlers.clear()

    @staticmethod
    def create_event(
        event_type: str,
        aggregate_id: str,
        aggregate_type: str,
        event_data: Any,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DomainEvent:
        """Crear un evento de dominio"""
        return DomainEvent(
            event_type=event_type,
            aggregate_id=aggregate_id,
            aggregate_type=aggregate_type,
            event_data=event_data,
            timestamp=datetime.utcnow(),
            user_id=user_id,
            metadata=metadata
        )

    async def publish_user_event(
        self,
        event_type: str,
        user_id: str,
        event_data: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Publicar evento de usuario"""
        event = self.create_event(
            event_type,
            user_id,
            'User',
            event_data,
            user_id,
            metadata
        )
        await self.publish(event)

    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del event bus"""
        total_handlers = sum(len(handlers) for handlers in self._handlers.values())
        
        return {
            "total_events": len(self._handlers),
            "total_handlers": total_handlers,
            "event_types": self.get_registered_events(),
            "max_listeners": self._max_listeners
        }