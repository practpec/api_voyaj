from abc import ABC, abstractmethod
from typing import List, Optional
from ..friendship import Friendship


class IFriendshipRepository(ABC):
    
    @abstractmethod
    async def create(self, friendship: Friendship) -> Friendship:
        """Crear nueva amistad"""
        pass

    @abstractmethod
    async def find_by_id(self, friendship_id: str) -> Optional[Friendship]:
        """Buscar amistad por ID"""
        pass

    @abstractmethod
    async def update(self, friendship: Friendship) -> Friendship:
        """Actualizar amistad"""
        pass

    @abstractmethod
    async def delete(self, friendship_id: str) -> bool:
        """Eliminar amistad (soft delete)"""
        pass

    @abstractmethod
    async def find_between_users(self, user_id: str, friend_id: str) -> Optional[Friendship]:
        """Buscar amistad entre dos usuarios específicos"""
        pass

    @abstractmethod
    async def find_accepted_between_users(self, user_id: str, friend_id: str) -> Optional[Friendship]:
        """Buscar amistad aceptada entre dos usuarios"""
        pass

    @abstractmethod
    async def find_pending_between_users(self, user_id: str, friend_id: str) -> Optional[Friendship]:
        """Buscar solicitud pendiente entre dos usuarios"""
        pass

    @abstractmethod
    async def find_user_friends(
        self, 
        user_id: str, 
        page: int = 1, 
        limit: int = 20
    ) -> tuple[List[Friendship], int]:
        """Buscar amigos aceptados de un usuario con paginación"""
        pass

    @abstractmethod
    async def find_pending_requests_received(
        self, 
        user_id: str, 
        page: int = 1, 
        limit: int = 20
    ) -> tuple[List[Friendship], int]:
        """Buscar solicitudes pendientes recibidas por un usuario"""
        pass

    @abstractmethod
    async def find_pending_requests_sent(
        self, 
        user_id: str, 
        page: int = 1, 
        limit: int = 20
    ) -> tuple[List[Friendship], int]:
        """Buscar solicitudes pendientes enviadas por un usuario"""
        pass

    @abstractmethod
    async def count_user_friends(self, user_id: str) -> int:
        """Contar amigos de un usuario"""
        pass

    @abstractmethod
    async def count_pending_requests_received(self, user_id: str) -> int:
        """Contar solicitudes pendientes recibidas"""
        pass

    @abstractmethod
    async def count_pending_requests_sent(self, user_id: str) -> int:
        """Contar solicitudes pendientes enviadas"""
        pass

    @abstractmethod
    async def find_accepted_friends_ids(self, user_id: str) -> List[str]:
        """Obtener IDs de amigos aceptados de un usuario"""
        pass