# src/modules/friendships/application/use_cases/get_friends.py
from typing import List
from ..dtos.friendship_dto import FriendListResponseDTO, FriendshipDTOMapper
from ...domain.friendship_service import FriendshipService
from ...domain.interfaces.friendship_repository import IFriendshipRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from shared.utils.pagination_utils import PaginatedResponse


class GetFriendsUseCase:
    def __init__(
        self,
        friendship_repository: IFriendshipRepository,
        user_repository: IUserRepository,
        friendship_service: FriendshipService
    ):
        self._friendship_repository = friendship_repository
        self._user_repository = user_repository
        self._friendship_service = friendship_service

    async def execute(
        self, 
        user_id: str, 
        page: int = 1, 
        limit: int = 20
    ) -> PaginatedResponse[FriendListResponseDTO]:
        """Obtener lista de amigos de un usuario"""
        # Obtener amistades aceptadas con paginación
        friendships, total = await self._friendship_repository.find_user_friends(user_id, page, limit)

        if not friendships:
            return PaginatedResponse(
                data=[],
                total=0,
                page=page,
                limit=limit,
                total_pages=0
            )

        # Obtener información de los amigos
        friend_responses: List[FriendListResponseDTO] = []
        
        for friendship in friendships:
            # Determinar qué usuario es el amigo
            friend_id = friendship.friend_id if friendship.user_id == user_id else friendship.user_id
            
            # Obtener información del amigo
            friend_user = await self._user_repository.find_by_id(friend_id)
            if not friend_user:
                continue

            # Obtener cantidad de amigos en común
            mutual_friends_count = await self._friendship_service.get_mutual_friends_count(
                user_id, 
                friend_id
            )

            # Mapear a DTO de respuesta
            friend_response = FriendshipDTOMapper.to_friend_list_response(
                friendship.to_public_data(),
                friend_user.to_public_data(),
                mutual_friends_count
            )
            
            friend_responses.append(friend_response)

        total_pages = (total + limit - 1) // limit

        return PaginatedResponse(
            data=friend_responses,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )