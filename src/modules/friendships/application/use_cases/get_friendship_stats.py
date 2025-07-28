# src/modules/friendships/application/use_cases/get_friendship_stats.py
from ..dtos.friendship_dto import FriendshipStatsDTO
from ...domain.interfaces.IFriendshipRepository import IFriendshipRepository


class GetFriendshipStatsUseCase:
    def __init__(self, friendship_repository: IFriendshipRepository):
        self._friendship_repository = friendship_repository

    async def execute(self, user_id: str) -> FriendshipStatsDTO:
        """Obtener estadísticas de amistad de un usuario"""
        # Ejecutar consultas en paralelo para optimizar rendimiento
        import asyncio
        
        results = await asyncio.gather(
            self._friendship_repository.count_user_friends(user_id),
            self._friendship_repository.count_pending_requests_received(user_id),
            self._friendship_repository.count_pending_requests_sent(user_id),
            return_exceptions=True
        )

        # Manejar posibles errores en las consultas
        total_friends = results[0] if not isinstance(results[0], Exception) else 0
        pending_received = results[1] if not isinstance(results[1], Exception) else 0
        pending_sent = results[2] if not isinstance(results[2], Exception) else 0

        return FriendshipStatsDTO(
            total_friends=total_friends,
            pending_requests_received=pending_received,
            pending_requests_sent=pending_sent
        )