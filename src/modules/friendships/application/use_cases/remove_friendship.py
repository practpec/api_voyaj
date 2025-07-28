# src/modules/friendships/application/use_cases/remove_friendship.py
from ...domain.friendship_service import FriendshipService
from ...domain.interfaces.IFriendshipRepository import IFriendshipRepository
from shared.errors.custom_errors import NotFoundError


class RemoveFriendshipUseCase:
    def __init__(
        self,
        friendship_repository: IFriendshipRepository,
        friendship_service: FriendshipService
    ):
        self._friendship_repository = friendship_repository
        self._friendship_service = friendship_service

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

        return True