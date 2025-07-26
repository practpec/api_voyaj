# src/modules/activity_votes/domain/interfaces/activity_vote_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..activity_vote import ActivityVote


class IActivityVoteRepository(ABC):
    
    @abstractmethod
    async def create(self, vote: ActivityVote) -> ActivityVote:
        """Crear nuevo voto"""
        pass

    @abstractmethod
    async def find_by_id(self, vote_id: str) -> Optional[ActivityVote]:
        """Buscar voto por ID"""
        pass

    @abstractmethod
    async def find_by_activity_and_user(self, activity_id: str, user_id: str) -> Optional[ActivityVote]:
        """Buscar voto específico de usuario para una actividad"""
        pass

    @abstractmethod
    async def update(self, vote: ActivityVote) -> ActivityVote:
        """Actualizar voto"""
        pass

    @abstractmethod
    async def delete(self, vote_id: str) -> bool:
        """Eliminar voto (soft delete)"""
        pass

    @abstractmethod
    async def find_by_activity_id(self, activity_id: str) -> List[ActivityVote]:
        """Buscar todos los votos de una actividad"""
        pass

    @abstractmethod
    async def find_by_user_id(self, user_id: str, trip_id: Optional[str] = None) -> List[ActivityVote]:
        """Buscar votos de un usuario"""
        pass

    @abstractmethod
    async def find_by_trip_id(self, trip_id: str) -> List[ActivityVote]:
        """Buscar votos de un viaje"""
        pass

    @abstractmethod
    async def count_by_activity_id(self, activity_id: str) -> int:
        """Contar votos de una actividad"""
        pass

    @abstractmethod
    async def count_by_vote_type(self, activity_id: str, vote_type: str) -> int:
        """Contar votos por tipo para una actividad"""
        pass

    @abstractmethod
    async def get_activity_vote_stats(self, activity_id: str) -> Dict[str, int]:
        """Obtener estadísticas de votos para una actividad"""
        pass

    @abstractmethod
    async def get_trip_vote_rankings(self, trip_id: str) -> List[Dict[str, Any]]:
        """Obtener ranking de actividades por votos en un viaje"""
        pass

    @abstractmethod
    async def get_trip_polls(self, trip_id: str) -> List[Dict[str, Any]]:
        """Obtener encuestas activas de un viaje"""
        pass

    @abstractmethod
    async def find_with_filters(
        self, 
        filters: Dict[str, Any], 
        page: int = 1, 
        limit: int = 20
    ) -> tuple[List[ActivityVote], int]:
        """Buscar votos con filtros y paginación"""
        pass