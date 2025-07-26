# src/modules/diary_recommendations/domain/interfaces/diary_recommendation_repository_interface.py
from abc import ABC, abstractmethod
from typing import List, Optional
from ..diary_recommendation import DiaryRecommendation


class DiaryRecommendationRepositoryInterface(ABC):

    @abstractmethod
    async def save(self, recommendation: DiaryRecommendation) -> None:
        """Guardar recomendación"""
        pass

    @abstractmethod
    async def find_by_id(self, recommendation_id: str) -> Optional[DiaryRecommendation]:
        """Buscar recomendación por ID"""
        pass

    @abstractmethod
    async def find_by_diary_entry_id(self, diary_entry_id: str) -> List[DiaryRecommendation]:
        """Buscar recomendaciones por entrada de diario"""
        pass

    @abstractmethod
    async def update(self, recommendation: DiaryRecommendation) -> None:
        """Actualizar recomendación"""
        pass

    @abstractmethod
    async def delete(self, recommendation_id: str) -> None:
        """Eliminar recomendación (soft delete)"""
        pass

    @abstractmethod
    async def exists_by_id(self, recommendation_id: str) -> bool:
        """Verificar si existe recomendación por ID"""
        pass

    @abstractmethod
    async def count_by_diary_entry_id(self, diary_entry_id: str) -> int:
        """Contar recomendaciones activas por entrada de diario"""
        pass