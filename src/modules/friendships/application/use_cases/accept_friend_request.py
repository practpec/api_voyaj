from ..dtos.friendship_dto import FriendshipResponseDTO, FriendshipDTOMapper
from domain.friendship_service import FriendshipService
from domain.friendship_events import FriendRequestAcceptedEvent
from domain.interfaces.friendship_repository import IFriendshipRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from shared.events.event_bus import EventBus
from shared.errors.custom_errors import NotFoundError


class AcceptFriendRequestUseCase:
    def __init__(
        self,
        friendship_repository: IFriendshipRepository,
        user_repository: IUserRepository,
        friendship_service: FriendshipService,
        event_bus: EventBus
    ):
        self._friendship_repository = friendship_repository
        self._user_repository = user_repository
        self._friendship_service = friendship_service
        self._event_bus = event_bus

    async def execute(self, friendship_id: str, user_id: str) -> FriendshipResponseDTO:
        """Aceptar solicitud de amistad"""
        # Buscar la solicitud de amistad
        friendship = await self._friendship_repository.find_by_id(friendship_id)
        if not friendship:
            raise NotFoundError("Solicitud de amistad no encontrada")

        # Validar que el usuario puede aceptar esta solicitud
        await self._friendship_service.validate_friendship_action(friendship, user_id, "accept")

        # Aceptar la solicitud
        friendship.accept()

        # Guardar cambios
        updated_friendship = await self._friendship_repository.update(friendship)

        # Emitir evento de dominio
        event = FriendRequestAcceptedEvent(
            requester_id=friendship.user_id,
            recipient_id=friendship.friend_id,
            friendship_id=friendship.id
        )
        await self._event_bus.publish(event)

        # Obtener información de ambos usuarios para la respuesta
        requester_user = await self._user_repository.find_by_id(friendship.user_id)
        recipient_user = await self._user_repository.find_by_id(friendship.friend_id)

        return FriendshipDTOMapper.to_friendship_response(
            updated_friendship.to_public_data(),
            requester_user.to_public_data() if requester_user else None,
            recipient_user.to_public_data() if recipient_user else None
        )