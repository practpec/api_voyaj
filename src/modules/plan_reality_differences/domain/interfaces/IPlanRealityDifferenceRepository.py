from abc import ABC, abstractmethod
from typing import List, Optional
from ..PlanRealityDifference import PlanRealityDifferenceData


class IPlanRealityDifferenceRepository(ABC):
    """Interfaz del repositorio de diferencias plan vs realidad"""

    @abstractmethod
    async def save(self, difference: PlanRealityDifferenceData) -> PlanRealityDifferenceData:
        """Guardar diferencia"""
        pass

    @abstractmethod
    async def find_by_id(self, difference_id: str) -> Optional[PlanRealityDifferenceData]:
        """Buscar diferencia por ID"""
        pass

    @abstractmethod
    async def find_by_trip_id(self, trip_id: str) -> List[PlanRealityDifferenceData]:
        """Buscar diferencias por ID del viaje"""
        pass

    @abstractmethod
    async def find_by_day_id(self, day_id: str) -> List[PlanRealityDifferenceData]:
        """Buscar diferencias por ID del día"""
        pass

    @abstractmethod
    async def find_by_activity_id(self, activity_id: str) -> List[PlanRealityDifferenceData]:
        """Buscar diferencias por ID de la actividad"""
        pass

    @abstractmethod
    async def find_by_trip_and_metric(self, trip_id: str, metric: str) -> List[PlanRealityDifferenceData]:
        """Buscar diferencias por viaje y métrica específica"""
        pass

    @abstractmethod
    async def update(self, difference: PlanRealityDifferenceData) -> PlanRealityDifferenceData:
        """Actualizar diferencia"""
        pass

    @abstractmethod
    async def delete(self, difference_id: str) -> bool:
        """Eliminar diferencia (soft delete)"""
        pass

    @abstractmethod
    async def exists_by_id(self, difference_id: str) -> bool:
        """Verificar si existe una diferencia por ID"""
        pass