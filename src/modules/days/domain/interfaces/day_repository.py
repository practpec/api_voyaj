from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import date
from ..Day import Day


class IDayRepository(ABC):
    
    @abstractmethod
    async def create(self, day: Day) -> Day:
        """Crear nuevo día"""
        pass

    @abstractmethod
    async def find_by_id(self, day_id: str) -> Optional[Day]:
        """Buscar día por ID"""
        pass

    @abstractmethod
    async def update(self, day: Day) -> Day:
        """Actualizar día"""
        pass

    @abstractmethod
    async def delete(self, day_id: str) -> bool:
        """Eliminar día (soft delete)"""
        pass

    @abstractmethod
    async def find_by_trip_id(self, trip_id: str) -> List[Day]:
        """Buscar días por viaje"""
        pass

    @abstractmethod
    async def find_by_trip_id_ordered(self, trip_id: str) -> List[Day]:
        """Buscar días por viaje ordenados por fecha"""
        pass

    @abstractmethod
    async def find_by_trip_and_date(self, trip_id: str, day_date: date) -> Optional[Day]:
        """Buscar día específico por viaje y fecha"""
        pass

    @abstractmethod
    async def find_by_date_range(
        self, 
        trip_id: str, 
        start_date: date, 
        end_date: date
    ) -> List[Day]:
        """Buscar días en rango de fechas"""
        pass

    @abstractmethod
    async def find_with_notes(self, trip_id: str) -> List[Day]:
        """Buscar días que tienen notas"""
        pass

    @abstractmethod
    async def find_with_filters(
        self, 
        filters: Dict[str, Any], 
        page: int = 1, 
        limit: int = 20
    ) -> tuple[List[Day], int]:
        """Buscar días con filtros y paginación"""
        pass

    @abstractmethod
    async def count_by_trip_id(self, trip_id: str) -> int:
        """Contar días por viaje"""
        pass

    @abstractmethod
    async def count_with_notes(self, trip_id: str) -> int:
        """Contar días con notas por viaje"""
        pass

    @abstractmethod
    async def exists_by_trip_and_date(self, trip_id: str, day_date: date) -> bool:
        """Verificar si existe día para fecha específica"""
        pass

    @abstractmethod
    async def delete_by_trip_id(self, trip_id: str) -> bool:
        """Eliminar todos los días de un viaje"""
        pass

    @abstractmethod
    async def bulk_create(self, days: List[Day]) -> List[Day]:
        """Crear múltiples días en lote"""
        pass

    @abstractmethod
    async def get_trip_day_statistics(self, trip_id: str) -> Dict[str, Any]:
        """Obtener estadísticas de días del viaje"""
        pass