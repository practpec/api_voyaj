# src/modules/diary_recommendations/application/use_cases/create_diary_recommendation.py
from typing import Dict, Any
from ..dtos.diary_recommendation_dto import CreateDiaryRecommendationDTO, DiaryRecommendationResponseDTO
from ...domain.diary_recommendation_service import DiaryRecommendationService
from shared.errors.custom_errors import ValidationError, NotFoundError, ForbiddenError


class CreateDiaryRecommendationUseCase:
    def __init__(self, recommendation_service: DiaryRecommendationService):
        self._recommendation_service = recommendation_service

    async def execute(
        self, 
        dto: CreateDiaryRecommendationDTO, 
        current_user: Dict[str, Any]
    ) -> DiaryRecommendationResponseDTO:
        """Ejecutar creación de recomendación"""
        try:
            recommendation = await self._recommendation_service.create_recommendation(
                diary_entry_id=dto.diary_entry_id,
                note=dto.note,
                recommendation_type=dto.type
            )

            return DiaryRecommendationResponseDTO(
                id=recommendation.id,
                diary_entry_id=recommendation.diary_entry_id,
                note=recommendation.note,
                type=recommendation.type.value,
                created_at=recommendation.created_at,
                updated_at=recommendation.updated_at
            )

        except ValidationError as e:
            raise ValidationError(str(e))
        except NotFoundError as e:
            raise NotFoundError(str(e))
        except Exception as e:
            raise ValidationError(f"Error al crear recomendación: {str(e)}")