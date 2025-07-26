# src/modules/diary_recommendations/infrastructure/controllers/diary_recommendation_controller.py
from fastapi import HTTPException
from typing import Dict, Any
from ...application.dtos.diary_recommendation_dto import (
    CreateDiaryRecommendationDTO, UpdateDiaryRecommendationDTO,
    DiaryRecommendationResponseDTO, DiaryEntryRecommendationsResponseDTO
)
from ...application.use_cases.create_diary_recommendation import CreateDiaryRecommendationUseCase
from ...application.use_cases.get_diary_recommendation import GetDiaryRecommendationUseCase
from ...application.use_cases.get_diary_entry_recommendations import GetDiaryEntryRecommendationsUseCase
from ...application.use_cases.update_diary_recommendation import UpdateDiaryRecommendationUseCase
from ...application.use_cases.delete_diary_recommendation import DeleteDiaryRecommendationUseCase
from shared.errors.custom_errors import ValidationError, NotFoundError, ForbiddenError


class DiaryRecommendationController:
    def __init__(
        self,
        create_recommendation_use_case: CreateDiaryRecommendationUseCase,
        get_recommendation_use_case: GetDiaryRecommendationUseCase,
        get_entry_recommendations_use_case: GetDiaryEntryRecommendationsUseCase,
        update_recommendation_use_case: UpdateDiaryRecommendationUseCase,
        delete_recommendation_use_case: DeleteDiaryRecommendationUseCase
    ):
        self._create_recommendation_use_case = create_recommendation_use_case
        self._get_recommendation_use_case = get_recommendation_use_case
        self._get_entry_recommendations_use_case = get_entry_recommendations_use_case
        self._update_recommendation_use_case = update_recommendation_use_case
        self._delete_recommendation_use_case = delete_recommendation_use_case

    async def create_recommendation(
        self, 
        dto: CreateDiaryRecommendationDTO, 
        current_user: Dict[str, Any]
    ) -> DiaryRecommendationResponseDTO:
        """Crear nueva recomendación"""
        try:
            return await self._create_recommendation_use_case.execute(dto, current_user)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def get_recommendation(
        self, 
        recommendation_id: str, 
        current_user: Dict[str, Any]
    ) -> DiaryRecommendationResponseDTO:
        """Obtener recomendación por ID"""
        try:
            return await self._get_recommendation_use_case.execute(recommendation_id, current_user)
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def get_diary_entry_recommendations(
        self, 
        diary_entry_id: str, 
        current_user: Dict[str, Any]
    ) -> DiaryEntryRecommendationsResponseDTO:
        """Obtener recomendaciones por entrada de diario"""
        try:
            return await self._get_entry_recommendations_use_case.execute(diary_entry_id, current_user)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def update_recommendation(
        self, 
        recommendation_id: str,
        dto: UpdateDiaryRecommendationDTO, 
        current_user: Dict[str, Any]
    ) -> DiaryRecommendationResponseDTO:
        """Actualizar recomendación"""
        try:
            return await self._update_recommendation_use_case.execute(recommendation_id, dto, current_user)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def delete_recommendation(
        self, 
        recommendation_id: str, 
        current_user: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Eliminar recomendación"""
        try:
            return await self._delete_recommendation_use_case.execute(recommendation_id, current_user)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")