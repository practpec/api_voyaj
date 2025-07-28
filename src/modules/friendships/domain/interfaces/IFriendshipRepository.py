# src/modules/friendships/domain/interfaces/IFriendshipRepository.py
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from ..Friendship import Friendship


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
    async def find_user_friends(
        self, 
        user_id: str, 
        page: int = 1, 
        limit: int = 20
    ) -> Tuple[List[Friendship], int]:
        """Buscar amigos aceptados de un usuario con paginación"""
        pass

    @abstractmethod
    async def find_pending_requests_received(
        self, 
        user_id: str, 
        page: int = 1, 
        limit: int = 20
    ) -> Tuple[List[Friendship], int]:
        """Buscar solicitudes pendientes recibidas por un usuario"""
        pass

    @abstractmethod
    async def find_pending_requests_sent(
        self, 
        user_id: str, 
        page: int = 1, 
        limit: int = 20
    ) -> Tuple[List[Friendship], int]:
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

    @abstractmethod
    async def get_all_users_except(self, user_id: str, limit: int = 10) -> List[str]:
        """Obtener usuarios que no son amigos para sugerencias"""
        pass