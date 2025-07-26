# src/modules/photos/domain/interfaces/IPhotoRepository.py
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..Photo import Photo

class IPhotoRepository(ABC):
    """Interfaz del repositorio de fotos"""

    @abstractmethod
    async def create(self, photo: Photo) -> Photo:
        """Crear nueva foto"""
        pass

    @abstractmethod
    async def get_by_id(self, photo_id: str) -> Optional[Photo]:
        """Obtener foto por ID"""
        pass

    @abstractmethod
    async def get_by_trip_id(
        self, 
        trip_id: str, 
        limit: int = 20, 
        offset: int = 0,
        day_id: Optional[str] = None
    ) -> List[Photo]:
        """Obtener fotos de un viaje"""
        pass

    @abstractmethod
    async def get_by_day_id(self, day_id: str) -> List[Photo]:
        """Obtener fotos de un día específico"""
        pass

    @abstractmethod
    async def get_by_diary_entry_id(self, diary_entry_id: str) -> List[Photo]:
        """Obtener fotos de una entrada de diario"""
        pass

    @abstractmethod
    async def update(self, photo: Photo) -> Photo:
        """Actualizar foto"""
        pass

    @abstractmethod
    async def delete(self, photo_id: str) -> bool:
        """Eliminar foto"""
        pass

    @abstractmethod
    async def count_by_trip_id(self, trip_id: str) -> int:
        """Contar fotos de un viaje"""
        pass

    @abstractmethod
    async def get_trip_photos_stats(self, trip_id: str) -> Dict[str, Any]:
        """Obtener estadísticas de fotos del viaje"""
        pass

    @abstractmethod
    async def get_most_liked_photos(self, trip_id: str, limit: int = 5) -> List[Photo]:
        """Obtener fotos con más likes"""
        pass

    @abstractmethod
    async def search_photos(
        self, 
        trip_id: str, 
        query: str, 
        limit: int = 20, 
        offset: int = 0
    ) -> List[Photo]:
        """Buscar fotos por título, descripción o tags"""
        pass