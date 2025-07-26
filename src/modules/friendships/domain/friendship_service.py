from typing import List, Optional
from .friendship import Friendship
from .interfaces.friendship_repository import IFriendshipRepository
from shared.errors.custom_errors import NotFoundError, ValidationError, ConflictError


class FriendshipService:
    def __init__(self, friendship_repository: IFriendshipRepository):
        self._friendship_repository = friendship_repository

    async def validate_friendship_creation(self, user_id: str, friend_id: str) -> None:
        """Validar que se puede crear una nueva amistad"""
        if user_id == friend_id:
            raise ValidationError("No puedes enviarte una solicitud de amistad a ti mismo")

        # Verificar si ya existe una relación entre estos usuarios
        existing_friendship = await self._friendship_repository.find_between_users(user_id, friend_id)
        
        if existing_friendship:
            if existing_friendship.is_pending():
                raise ConflictError("Ya existe una solicitud de amistad pendiente entre estos usuarios")
            elif existing_friendship.is_accepted():
                raise ConflictError("Ya son amigos")
            elif existing_friendship.is_rejected():
                # Permitir crear nueva solicitud si la anterior fue rechazada
                pass

    async def validate_friendship_action(
        self, 
        friendship: Friendship, 
        user_id: str, 
        action: str
    ) -> None:
        """Validar que un usuario puede realizar una acción sobre una amistad"""
        if action == "accept":
            # Solo el destinatario puede aceptar la solicitud
            if friendship.friend_id != user_id:
                raise ValidationError("Solo el destinatario puede aceptar la solicitud de amistad")
        elif action == "reject":
            # Solo el destinatario puede rechazar la solicitud
            if friendship.friend_id != user_id:
                raise ValidationError("Solo el destinatario puede rechazar la solicitud de amistad")
        elif action == "cancel":
            # Solo el remitente puede cancelar la solicitud
            if friendship.user_id != user_id:
                raise ValidationError("Solo el remitente puede cancelar la solicitud de amistad")
        elif action == "remove":
            # Cualquiera de los dos puede eliminar la amistad
            if friendship.user_id != user_id and friendship.friend_id != user_id:
                raise ValidationError("No tienes permisos para eliminar esta amistad")

    async def get_mutual_friends_count(self, user_id: str, other_user_id: str) -> int:
        """Obtener cantidad de amigos en común entre dos usuarios"""
        user_friends = await self._friendship_repository.find_accepted_friends_ids(user_id)
        other_friends = await self._friendship_repository.find_accepted_friends_ids(other_user_id)
        
        mutual_friends = set(user_friends) & set(other_friends)
        return len(mutual_friends)

    async def suggest_friends(self, user_id: str, limit: int = 10) -> List[str]:
        """Sugerir amigos basado en amigos en común"""
        user_friends = await self._friendship_repository.find_accepted_friends_ids(user_id)
        
        if not user_friends:
            return []

        # Obtener amigos de amigos
        potential_friends = set()
        for friend_id in user_friends:
            friend_friends = await self._friendship_repository.find_accepted_friends_ids(friend_id)
            potential_friends.update(friend_friends)

        # Remover al usuario actual y sus amigos existentes
        potential_friends.discard(user_id)
        potential_friends -= set(user_friends)

        # Limitar resultados
        return list(potential_friends)[:limit]