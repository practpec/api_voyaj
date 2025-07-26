from ..dtos.friendship_dto import SendFriendRequestDTO, FriendshipResponseDTO, FriendshipDTOMapper
from domain.friendship import Friendship
from domain.friendship_service import FriendshipService
from domain.friendship_events import FriendRequestSentEvent
from domain.interfaces.friendship_repository import IFriendshipRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from shared.events.event_bus import EventBus
from shared.errors.custom_errors import NotFoundError


class SendFriendRequestUseCase:
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

    async def execute(self, dto: SendFriendRequestDTO, requester_id: str) -> FriendshipResponseDTO:
        """Enviar solicitud de amistad"""
        # Verificar que el usuario destinatario existe
        recipient_user = await self._user_repository.find_by_id(dto.friend_id)
        if not recipient_user:
            raise NotFoundError("Usuario no encontrado")

        # Validar que se puede crear la amistad
        await self._friendship_service.validate_friendship_creation(requester_id, dto.friend_id)

        # Crear nueva solicitud de amistad
        friendship = Friendship.create(requester_id, dto.friend_id)

        # Guardar en repositorio
        created_friendship = await self._friendship_repository.create(friendship)

        # Emitir evento de dominio
        event = FriendRequestSentEvent(
            requester_id=requester_id,
            recipient_id=dto.friend_id,
            friendship_id=created_friendship.id
        )
        await self._event_bus.publish(event)

        # Obtener información de usuarios para la respuesta
        requester_user = await self._user_repository.find_by_id(requester_id)
        
        return FriendshipDTOMapper.to_friendship_response(
            created_friendship.to_public_data(),
            requester_user.to_public_data() if requester_user else None,
            recipient_user.to_public_data() if recipient_user else None
        )