# src/modules/diary_recommendations/application/use_cases/delete_diary_recommendation.py
from typing import Dict, Any
from ...domain.diary_recommendation_service import DiaryRecommendationService
from shared.errors.custom_errors import ValidationError


class DeleteDiaryRecommendationUseCase:
    def __init__(self, recommendation_service: DiaryRecommendationService):
        self._recommendation_service = recommendation_service

    async def execute(
        self, 
        recommendation_id: str, 
        current_user: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Ejecutar eliminación de recomendación"""
        if not recommendation_id:
            raise ValidationError("ID de recomendación es requerido")

        try:
            success = await self._recommendation_service.delete_recommendation(recommendation_id)
            
            if not success:
                raise ValidationError("No se pudo eliminar la recomendación")

            return {
                "success": True,
                "message": "Recomendación eliminada exitosamente"
            }

        except Exception as e:
            raise ValidationError(f"Error al eliminar recomendación: {str(e)}")