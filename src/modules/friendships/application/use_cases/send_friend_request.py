# src/modules/friendships/application/use_cases/send_friend_request.py
from ..dtos.friendship_dto import SendFriendRequestDTO, FriendshipResponseDTO, FriendshipDTOMapper
from ...domain.Friendship import Friendship
from ...domain.friendship_service import FriendshipService
from ...domain.interfaces.IFriendshipRepository import IFriendshipRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from shared.errors.custom_errors import NotFoundError


class SendFriendRequestUseCase:
    def __init__(
        self,
        friendship_repository: IFriendshipRepository,
        user_repository: IUserRepository,
        friendship_service: FriendshipService
    ):
        self._friendship_repository = friendship_repository
        self._user_repository = user_repository
        self._friendship_service = friendship_service

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

        # Obtener información de usuarios para la respuesta
        requester_user = await self._user_repository.find_by_id(requester_id)
        
        return FriendshipDTOMapper.to_friendship_response(
            created_friendship.to_public_data(),
            requester_user.to_public_dict() if requester_user else None,
            recipient_user.to_public_dict() if recipient_user else None
        )