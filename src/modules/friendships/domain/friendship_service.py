# src/modules/friendships/domain/friendship_service.py
from typing import List
from .Friendship import Friendship
from .interfaces.IFriendshipRepository import IFriendshipRepository
from shared.errors.custom_errors import ValidationError, ConflictError


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
        """Sugerir amigos basado en usuarios que no son amigos"""
        # Obtener amigos actuales
        user_friends = await self._friendship_repository.find_accepted_friends_ids(user_id)
        
        # Obtener todos los usuarios excepto el actual y sus amigos
        suggested_users = await self._friendship_repository.get_all_users_except(user_id, limit * 3)
        
        # Filtrar usuarios que ya son amigos
        potential_friends = []
        for suggested_id in suggested_users:
            if suggested_id not in user_friends:
                # Verificar que no existe solicitud pendiente
                existing_friendship = await self._friendship_repository.find_between_users(user_id, suggested_id)
                if not existing_friendship:
                    potential_friends.append(suggested_id)
                    
                    if len(potential_friends) >= limit:
                        break
        
        return potential_friends