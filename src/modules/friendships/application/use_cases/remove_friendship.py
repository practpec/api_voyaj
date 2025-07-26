from domain.friendship_service import FriendshipService
from domain.friendship_events import FriendshipRemovedEvent
from domain.interfaces.friendship_repository import IFriendshipRepository
from shared.events.event_bus import EventBus
from shared.errors.custom_errors import NotFoundError


class RemoveFriendshipUseCase:
    def __init__(
        self,
        friendship_repository: IFriendshipRepository,
        friendship_service: FriendshipService,
        event_bus: EventBus
    ):
        self._friendship_repository = friendship_repository
        self._friendship_service = friendship_service
        self._event_bus = event_bus

    async def execute(self, friendship_id: str, user_id: str) -> bool:
        """Eliminar amistad existente"""
        # Buscar la amistad
        friendship = await self._friendship_repository.find_by_id(friendship_id)
        if not friendship:
            raise NotFoundError("Amistad no encontrada")

        # Validar que el usuario puede eliminar esta amistad
        await self._friendship_service.validate_friendship_action(friendship, user_id, "remove")

        # Verificar que la amistad está aceptada
        if not friendship.is_accepted():
            raise ValueError("Solo se pueden eliminar amistades aceptadas")

        # Eliminar la amistad (soft delete)
        friendship.remove()
        await self._friendship_repository.update(friendship)

        # Emitir evento de dominio
        event = FriendshipRemovedEvent(
            user_id=friendship.user_id,
            friend_id=friendship.friend_id,
            friendship_id=friendship.id
        )
        await self._event_bus.publish(event)

        return True