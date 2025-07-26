# src/modules/diary_recommendations/domain/diary_recommendation_service.py
from typing import List, Optional
from .diary_recommendation import DiaryRecommendation, DiaryRecommendationData, RecommendationType
from .interfaces.diary_recommendation_repository_interface import DiaryRecommendationRepositoryInterface
from modules.diary_entries.domain.interfaces.diary_entry_repository import IDiaryEntryRepository
from shared.errors.custom_errors import ValidationError, NotFoundError
import uuid
from datetime import datetime


class DiaryRecommendationService:
    def __init__(
        self,
        recommendation_repository: DiaryRecommendationRepositoryInterface,
        diary_entry_repository: IDiaryEntryRepository
    ):
        self._recommendation_repository = recommendation_repository
        self._diary_entry_repository = diary_entry_repository

    async def create_recommendation(
        self, 
        diary_entry_id: str, 
        note: str, 
        recommendation_type: RecommendationType
    ) -> DiaryRecommendation:
        """Crear nueva recomendación"""
        diary_entry = await self._diary_entry_repository.find_by_id(diary_entry_id)
        if not diary_entry:
            raise NotFoundError("Entrada de diario no encontrada")
        
        if diary_entry.is_deleted:
            raise ValidationError("No se puede crear recomendación para entrada eliminada")

        self._validate_recommendation_data(note, recommendation_type)

        data = DiaryRecommendationData(
            id=str(uuid.uuid4()),
            diary_entry_id=diary_entry_id,
            note=note.strip(),
            type=recommendation_type,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        recommendation = DiaryRecommendation(data)
        await self._recommendation_repository.save(recommendation)
        return recommendation

    async def get_recommendation_by_id(self, recommendation_id: str) -> Optional[DiaryRecommendation]:
        """Obtener recomendación por ID"""
        if not recommendation_id:
            return None
        
        recommendation = await self._recommendation_repository.find_by_id(recommendation_id)
        return recommendation if recommendation and not recommendation.is_deleted else None

    async def get_recommendations_by_diary_entry(self, diary_entry_id: str) -> List[DiaryRecommendation]:
        """Obtener recomendaciones por entrada de diario"""
        if not diary_entry_id:
            return []
        
        recommendations = await self._recommendation_repository.find_by_diary_entry_id(diary_entry_id)
        return [r for r in recommendations if not r.is_deleted]

    async def update_recommendation(
        self, 
        recommendation_id: str, 
        note: Optional[str] = None, 
        recommendation_type: Optional[RecommendationType] = None
    ) -> DiaryRecommendation:
        """Actualizar recomendación"""
        recommendation = await self._recommendation_repository.find_by_id(recommendation_id)
        if not recommendation:
            raise NotFoundError("Recomendación no encontrada")
        
        if recommendation.is_deleted:
            raise ValidationError("No se puede actualizar recomendación eliminada")

        if note is not None:
            self._validate_note(note)
            recommendation.update_note(note.strip())
        
        if recommendation_type is not None:
            recommendation.update_type(recommendation_type)

        await self._recommendation_repository.update(recommendation)
        return recommendation

    async def delete_recommendation(self, recommendation_id: str) -> bool:
        """Eliminar recomendación"""
        recommendation = await self._recommendation_repository.find_by_id(recommendation_id)
        if not recommendation:
            return False
        
        if recommendation.is_deleted:
            return True

        recommendation.mark_as_deleted()
        await self._recommendation_repository.update(recommendation)
        return True

    def _validate_recommendation_data(self, note: str, recommendation_type: RecommendationType) -> None:
        """Validar datos de recomendación"""
        self._validate_note(note)
        self._validate_type(recommendation_type)

    def _validate_note(self, note: str) -> None:
        """Validar nota de recomendación"""
        if not note or not note.strip():
            raise ValidationError("La nota es requerida")
        
        if len(note.strip()) < 3:
            raise ValidationError("La nota debe tener al menos 3 caracteres")
        
        if len(note.strip()) > 1000:
            raise ValidationError("La nota no puede exceder 1000 caracteres")

    def _validate_type(self, recommendation_type: RecommendationType) -> None:
        """Validar tipo de recomendación"""
        if not recommendation_type:
            raise ValidationError("El tipo de recomendación es requerido")
        
        if not isinstance(recommendation_type, RecommendationType):
            raise ValidationError("Tipo de recomendación inválido")