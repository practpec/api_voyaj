# src/modules/friendships/application/use_cases/get_friend_requests.py
from typing import List
from ..dtos.friendship_dto import FriendRequestResponseDTO, FriendshipDTOMapper
from ...domain.friendship_service import FriendshipService
from ...domain.interfaces.friendship_repository import IFriendshipRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from shared.utils.pagination_utils import PaginatedResponse


class GetFriendRequestsUseCase:
    def __init__(
        self,
        friendship_repository: IFriendshipRepository,
        user_repository: IUserRepository,
        friendship_service: FriendshipService
    ):
        self._friendship_repository = friendship_repository
        self._user_repository = user_repository
        self._friendship_service = friendship_service

    async def execute_received(
        self, 
        user_id: str, 
        page: int = 1, 
        limit: int = 20
    ) -> PaginatedResponse[FriendRequestResponseDTO]:
        """Obtener solicitudes de amistad recibidas"""
        # Obtener solicitudes pendientes recibidas
        friendships, total = await self._friendship_repository.find_pending_requests_received(
            user_id, page, limit
        )

        if not friendships:
            return PaginatedResponse(
                data=[],
                total=0,
                page=page,
                limit=limit,
                total_pages=0
            )

        # Obtener información de los remitentes
        request_responses: List[FriendRequestResponseDTO] = []
        
        for friendship in friendships:
            # Obtener información del remitente
            requester_user = await self._user_repository.find_by_id(friendship.user_id)
            if not requester_user:
                continue

            # Obtener cantidad de amigos en común
            mutual_friends_count = await self._friendship_service.get_mutual_friends_count(
                user_id, 
                friendship.user_id
            )

            # Mapear a DTO de respuesta
            request_response = FriendshipDTOMapper.to_friend_request_response(
                friendship.to_public_data(),
                requester_user.to_public_data(),
                mutual_friends_count
            )
            
            request_responses.append(request_response)

        total_pages = (total + limit - 1) // limit

        return PaginatedResponse(
            data=request_responses,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )

    async def execute_sent(
        self, 
        user_id: str, 
        page: int = 1, 
        limit: int = 20
    ) -> PaginatedResponse[FriendRequestResponseDTO]:
        """Obtener solicitudes de amistad enviadas"""
        # Obtener solicitudes pendientes enviadas
        friendships, total = await self._friendship_repository.find_pending_requests_sent(
            user_id, page, limit
        )

        if not friendships:
            return PaginatedResponse(
                data=[],
                total=0,
                page=page,
                limit=limit,
                total_pages=0
            )

        # Obtener información de los destinatarios
        request_responses: List[FriendRequestResponseDTO] = []
        
        for friendship in friendships:
            # Obtener información del destinatario
            recipient_user = await self._user_repository.find_by_id(friendship.friend_id)
            if not recipient_user:
                continue

            # Obtener cantidad de amigos en común
            mutual_friends_count = await self._friendship_service.get_mutual_friends_count(
                user_id, 
                friendship.friend_id
            )

            # Mapear a DTO de respuesta (usando recipient como "requester" para mostrar a quién se envió)
            request_response = FriendshipDTOMapper.to_friend_request_response(
                friendship.to_public_data(),
                recipient_user.to_public_data(),
                mutual_friends_count
            )
            
            request_responses.append(request_response)

        total_pages = (total + limit - 1) // limit

        return PaginatedResponse(
            data=request_responses,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )