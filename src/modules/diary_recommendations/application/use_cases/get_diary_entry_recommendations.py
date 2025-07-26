# src/modules/diary_recommendations/application/use_cases/get_diary_entry_recommendations.py
from typing import Dict, Any, List
from ..dtos.diary_recommendation_dto import DiaryEntryRecommendationsResponseDTO, DiaryRecommendationResponseDTO
from ...domain.diary_recommendation_service import DiaryRecommendationService
from shared.errors.custom_errors import ValidationError


class GetDiaryEntryRecommendationsUseCase:
    def __init__(self, recommendation_service: DiaryRecommendationService):
        self._recommendation_service = recommendation_service

    async def execute(
        self, 
        diary_entry_id: str, 
        current_user: Dict[str, Any]
    ) -> DiaryEntryRecommendationsResponseDTO:
        """Ejecutar obtención de recomendaciones por entrada de diario"""
        if not diary_entry_id:
            raise ValidationError("ID de entrada de diario es requerido")

        recommendations = await self._recommendation_service.get_recommendations_by_diary_entry(diary_entry_id)
        
        recommendation_dtos = [
            DiaryRecommendationResponseDTO(
                id=rec.id,
                diary_entry_id=rec.diary_entry_id,
                note=rec.note,
                type=rec.type.value,
                created_at=rec.created_at,
                updated_at=rec.updated_at
            )
            for rec in recommendations
        ]

        return DiaryEntryRecommendationsResponseDTO(
            diary_entry_id=diary_entry_id,
            recommendations=recommendation_dtos,
            total_count=len(recommendation_dtos)
        )