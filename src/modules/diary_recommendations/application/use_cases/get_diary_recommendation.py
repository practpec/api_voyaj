# src/modules/diary_recommendations/application/use_cases/get_diary_recommendation.py
from typing import Dict, Any
from ..dtos.diary_recommendation_dto import DiaryRecommendationResponseDTO
from ...domain.diary_recommendation_service import DiaryRecommendationService
from shared.errors.custom_errors import NotFoundError


class GetDiaryRecommendationUseCase:
    def __init__(self, recommendation_service: DiaryRecommendationService):
        self._recommendation_service = recommendation_service

    async def execute(
        self, 
        recommendation_id: str, 
        current_user: Dict[str, Any]
    ) -> DiaryRecommendationResponseDTO:
        """Ejecutar obtención de recomendación"""
        recommendation = await self._recommendation_service.get_recommendation_by_id(recommendation_id)
        
        if not recommendation:
            raise NotFoundError("Recomendación no encontrada")

        return DiaryRecommendationResponseDTO(
            id=recommendation.id,
            diary_entry_id=recommendation.diary_entry_id,
            note=recommendation.note,
            type=recommendation.type.value,
            created_at=recommendation.created_at,
            updated_at=recommendation.updated_at
        )