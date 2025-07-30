# src/modules/activities/domain/interfaces/activity_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..activity import Activity


class IActivityRepository(ABC):
    
    @abstractmethod
    async def create(self, activity: Activity) -> Activity:
        """Crear nueva actividad"""
        pass

    @abstractmethod
    async def find_by_id(self, activity_id: str) -> Optional[Activity]:
        """Buscar actividad por ID"""
        pass

    @abstractmethod
    async def update(self, activity: Activity) -> Activity:
        """Actualizar actividad"""
        pass

    @abstractmethod
    async def delete(self, activity_id: str) -> bool:
        """Eliminar actividad (soft delete)"""
        pass

    @abstractmethod
    async def find_by_day_id(self, day_id: str) -> List[Activity]:
        """Buscar actividades por día"""
        pass

    @abstractmethod
    async def find_by_day_id_ordered(self, day_id: str) -> List[Activity]:
        """Buscar actividades por día ordenadas"""
        pass

    @abstractmethod
    async def find_by_trip_id(self, trip_id: str) -> List[Activity]:
        """Buscar actividades por viaje"""
        pass

    @abstractmethod
    async def find_by_status(self, day_id: str, status: str) -> List[Activity]:
        """Buscar actividades por estado"""
        pass

    @abstractmethod
    async def find_by_category(self, day_id: str, category: str) -> List[Activity]:
        """Buscar actividades por categoría"""
        pass

    @abstractmethod
    async def find_by_user(self, user_id: str, trip_id: Optional[str] = None) -> List[Activity]:
        """Buscar actividades creadas por usuario"""
        pass

    @abstractmethod
    async def find_with_filters(
        self, 
        filters: Dict[str, Any], 
        page: int = 1, 
        limit: int = 20
    ) -> tuple[List[Activity], int]:
        """Buscar actividades con filtros y paginación"""
        pass

    @abstractmethod
    async def count_by_day_id(self, day_id: str) -> int:
        """Contar actividades por día"""
        pass

    @abstractmethod
    async def count_by_status(self, day_id: str, status: str) -> int:
        """Contar actividades por estado"""
        pass

    @abstractmethod
    async def count_by_trip_id(self, trip_id: str) -> int:
        """Contar actividades por viaje"""
        pass

    @abstractmethod
    async def get_next_order(self, day_id: str) -> int:
        """Obtener siguiente número de orden para el día"""
        pass