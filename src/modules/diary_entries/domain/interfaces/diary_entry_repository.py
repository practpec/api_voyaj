from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..diary_entry import DiaryEntry


class IDiaryEntryRepository(ABC):

    @abstractmethod
    async def create(self, diary_entry: DiaryEntry) -> DiaryEntry:
        """Crear nueva entrada de diario"""
        pass

    @abstractmethod
    async def find_by_id(self, entry_id: str) -> Optional[DiaryEntry]:
        """Buscar entrada por ID"""
        pass

    @abstractmethod
    async def update(self, diary_entry: DiaryEntry) -> DiaryEntry:
        """Actualizar entrada existente"""
        pass

    @abstractmethod
    async def delete(self, entry_id: str) -> bool:
        """Eliminar entrada (soft delete)"""
        pass

    @abstractmethod
    async def find_by_day_id(self, day_id: str) -> List[DiaryEntry]:
        """Buscar entradas por día"""
        pass

    @abstractmethod
    async def find_by_user_id(self, user_id: str) -> List[DiaryEntry]:
        """Buscar entradas por usuario"""
        pass

    @abstractmethod
    async def find_by_trip_id(self, trip_id: str) -> List[DiaryEntry]:
        """Buscar entradas por viaje"""
        pass

    @abstractmethod
    async def find_by_user_and_day(self, user_id: str, day_id: str) -> Optional[DiaryEntry]:
        """Buscar entrada específica de un usuario en un día"""
        pass

    @abstractmethod
    async def count_by_day_id(self, day_id: str) -> int:
        """Contar entradas por día"""
        pass

    @abstractmethod
    async def count_by_user_id(self, user_id: str) -> int:
        """Contar entradas por usuario"""
        pass

    @abstractmethod
    async def count_by_trip_id(self, trip_id: str) -> int:
        """Contar entradas por viaje"""
        pass

    @abstractmethod
    async def get_user_diary_statistics(self, user_id: str) -> Dict[str, Any]:
        """Obtener estadísticas del diario del usuario"""
        pass

    @abstractmethod
    async def get_trip_diary_statistics(self, trip_id: str) -> Dict[str, Any]:
        """Obtener estadísticas del diario del viaje"""
        pass

    @abstractmethod
    async def find_entries_with_emotions(self, trip_id: str) -> List[DiaryEntry]:
        """Buscar entradas que contengan emociones"""
        pass

    @abstractmethod
    async def find_entries_by_emotion_type(self, emotion_type: str, trip_id: Optional[str] = None) -> List[DiaryEntry]:
        """Buscar entradas por tipo de emoción"""
        pass

    @abstractmethod
    async def search_entries(
        self, 
        query: str, 
        user_id: Optional[str] = None,
        trip_id: Optional[str] = None,
        day_id: Optional[str] = None
    ) -> List[DiaryEntry]:
        """Buscar entradas por contenido"""
        pass

    @abstractmethod
    async def find_with_filters(
        self, 
        filters: Dict[str, Any], 
        page: int = 1, 
        limit: int = 20
    ) -> tuple[List[DiaryEntry], int]:
        """Buscar entradas con filtros y paginación"""
        pass

    @abstractmethod
    async def delete_by_day_id(self, day_id: str) -> bool:
        """Eliminar todas las entradas de un día"""
        pass

    @abstractmethod
    async def delete_by_trip_id(self, trip_id: str) -> bool:
        """Eliminar todas las entradas de un viaje"""
        pass

    @abstractmethod
    async def get_most_active_days(self, trip_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Obtener días con más actividad en el diario"""
        pass

    @abstractmethod
    async def get_emotion_trends(self, trip_id: str) -> Dict[str, Any]:
        """Obtener tendencias emocionales del viaje"""
        pass