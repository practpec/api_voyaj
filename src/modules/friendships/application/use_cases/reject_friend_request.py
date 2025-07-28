# src/modules/friendships/application/use_cases/reject_friend_request.py
from ..dtos.friendship_dto import FriendshipResponseDTO, FriendshipDTOMapper
from ...domain.friendship_service import FriendshipService
from ...domain.interfaces.IFriendshipRepository import IFriendshipRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from shared.errors.custom_errors import NotFoundError


class RejectFriendRequestUseCase:
    def __init__(
        self,
        friendship_repository: IFriendshipRepository,
        user_repository: IUserRepository,
        friendship_service: FriendshipService
    ):
        self._friendship_repository = friendship_repository
        self._user_repository = user_repository
        self._friendship_service = friendship_service

    async def execute(self, friendship_id: str, user_id: str) -> FriendshipResponseDTO:
        """Rechazar solicitud de amistad"""
        # Buscar la solicitud de amistad
        friendship = await self._friendship_repository.find_by_id(friendship_id)
        if not friendship:
            raise NotFoundError("Solicitud de amistad no encontrada")

        # Validar que el usuario puede rechazar esta solicitud
        await self._friendship_service.validate_friendship_action(friendship, user_id, "reject")

        # Rechazar la solicitud
        friendship.reject()

        # Guardar cambios
        updated_friendship = await self._friendship_repository.update(friendship)

        # Obtener información de ambos usuarios para la respuesta
        requester_user = await self._user_repository.find_by_id(friendship.user_id)
        recipient_user = await self._user_repository.find_by_id(friendship.friend_id)

        return FriendshipDTOMapper.to_friendship_response(
            updated_friendship.to_public_data(),
            requester_user.to_public_dict() if requester_user else None,
            recipient_user.to_public_dict() if recipient_user else None
        )