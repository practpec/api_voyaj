# src/modules/friendships/application/use_cases/get_friend_suggestions.py
from typing import List
from ..dtos.friendship_dto import FriendSuggestionDTO, FriendshipDTOMapper
from ...domain.friendship_service import FriendshipService
from ...domain.interfaces.IFriendshipRepository import IFriendshipRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository


class GetFriendSuggestionsUseCase:
    def __init__(
        self,
        friendship_repository: IFriendshipRepository,
        user_repository: IUserRepository,
        friendship_service: FriendshipService
    ):
        self._friendship_repository = friendship_repository
        self._user_repository = user_repository
        self._friendship_service = friendship_service

    async def execute(self, user_id: str, limit: int = 10) -> List[FriendSuggestionDTO]:
        """Obtener sugerencias de amigos simplificadas"""
        # Obtener IDs de usuarios sugeridos
        suggested_user_ids = await self._friendship_service.suggest_friends(user_id, limit)
        
        if not suggested_user_ids:
            return []

        # Obtener información de usuarios sugeridos
        suggestions: List[FriendSuggestionDTO] = []
        
        for suggested_id in suggested_user_ids:
            # Obtener información del usuario sugerido
            suggested_user = await self._user_repository.find_by_id(suggested_id)
            if not suggested_user:
                continue

            # Calcular amigos en común (simplificado)
            mutual_friends_count = await self._friendship_service.get_mutual_friends_count(
                user_id, 
                suggested_id
            )

            # Crear sugerencia
            suggestion = FriendshipDTOMapper.to_friend_suggestion(
                suggested_user.to_public_dict(),
                mutual_friends_count,
                f"{mutual_friends_count} amigo(s) en común" if mutual_friends_count > 0 else "Usuario recomendado"
            )
            suggestions.append(suggestion)

        # Ordenar por cantidad de amigos en común (descendente)
        suggestions.sort(key=lambda x: x.mutual_friends_count, reverse=True)
        
        return suggestions[:limit]