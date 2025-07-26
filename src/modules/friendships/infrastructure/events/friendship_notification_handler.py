from shared.events.event_bus import EventHandler
from shared.events.event_bus import EventBus
from domain.friendship_events import (
    FriendRequestSentEvent, 
    FriendRequestAcceptedEvent, 
    FriendRequestRejectedEvent
)


class FriendshipNotificationHandler(EventHandler):
    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus
        self._register_handlers()

    def _register_handlers(self):
        """Registrar manejadores de eventos"""
        self._event_bus.subscribe(FriendRequestSentEvent, self._handle_friend_request_sent)
        self._event_bus.subscribe(FriendRequestAcceptedEvent, self._handle_friend_request_accepted)
        self._event_bus.subscribe(FriendRequestRejectedEvent, self._handle_friend_request_rejected)

    async def _handle_friend_request_sent(self, event: FriendRequestSentEvent):
        """Manejar evento de solicitud de amistad enviada"""
        # Crear notificación para el destinatario
        # Implementación pendiente: integrar con módulo de notificaciones
        pass

    async def _handle_friend_request_accepted(self, event: FriendRequestAcceptedEvent):
        """Manejar evento de solicitud de amistad aceptada"""
        # Crear notificación para el remitente
        # Implementación pendiente: integrar con módulo de notificaciones
        pass

    async def _handle_friend_request_rejected(self, event: FriendRequestRejectedEvent):
        """Manejar evento de solicitud de amistad rechazada"""
        # Crear notificación para el remitente (opcional)
        # Implementación pendiente: integrar con módulo de notificaciones
        pass