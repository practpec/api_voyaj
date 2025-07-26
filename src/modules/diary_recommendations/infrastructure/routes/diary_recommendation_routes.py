# src/modules/diary_recommendations/infrastructure/routes/diary_recommendation_routes.py
from fastapi import APIRouter, Depends, Path
from ..controllers.diary_recommendation_controller import DiaryRecommendationController
from ...application.dtos.diary_recommendation_dto import (
    CreateDiaryRecommendationDTO, UpdateDiaryRecommendationDTO
)
from shared.middleware.AuthMiddleware import get_current_user
from shared.repositories.RepositoryFactory import RepositoryFactory

from ...application.use_cases.create_diary_recommendation import CreateDiaryRecommendationUseCase
from ...application.use_cases.get_diary_recommendation import GetDiaryRecommendationUseCase
from ...application.use_cases.get_diary_entry_recommendations import GetDiaryEntryRecommendationsUseCase
from ...application.use_cases.update_diary_recommendation import UpdateDiaryRecommendationUseCase
from ...application.use_cases.delete_diary_recommendation import DeleteDiaryRecommendationUseCase
from ...domain.diary_recommendation_service import DiaryRecommendationService

router = APIRouter()

def get_recommendation_controller():
    recommendation_repo = RepositoryFactory.get_diary_recommendation_repository()
    diary_entry_repo = RepositoryFactory.get_diary_entry_repository()
    
    recommendation_service = DiaryRecommendationService(
        recommendation_repository=recommendation_repo,
        diary_entry_repository=diary_entry_repo
    )
    
    create_recommendation_use_case = CreateDiaryRecommendationUseCase(
        recommendation_service=recommendation_service
    )
    
    get_recommendation_use_case = GetDiaryRecommendationUseCase(
        recommendation_service=recommendation_service
    )
    
    get_entry_recommendations_use_case = GetDiaryEntryRecommendationsUseCase(
        recommendation_service=recommendation_service
    )
    
    update_recommendation_use_case = UpdateDiaryRecommendationUseCase(
        recommendation_service=recommendation_service
    )
    
    delete_recommendation_use_case = DeleteDiaryRecommendationUseCase(
        recommendation_service=recommendation_service
    )
    
    return DiaryRecommendationController(
        create_recommendation_use_case=create_recommendation_use_case,
        get_recommendation_use_case=get_recommendation_use_case,
        get_entry_recommendations_use_case=get_entry_recommendations_use_case,
        update_recommendation_use_case=update_recommendation_use_case,
        delete_recommendation_use_case=delete_recommendation_use_case
    )

@router.post("/", summary="Crear recomendación")
async def create_recommendation(
    dto: CreateDiaryRecommendationDTO,
    current_user: dict = Depends(get_current_user),
    controller: DiaryRecommendationController = Depends(get_recommendation_controller)
):
    return await controller.create_recommendation(dto, current_user)

@router.get("/{recommendation_id}", summary="Obtener recomendación")
async def get_recommendation(
    recommendation_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    controller: DiaryRecommendationController = Depends(get_recommendation_controller)
):
    return await controller.get_recommendation(recommendation_id, current_user)

@router.get("/diary-entry/{diary_entry_id}", summary="Obtener recomendaciones por entrada")
async def get_diary_entry_recommendations(
    diary_entry_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    controller: DiaryRecommendationController = Depends(get_recommendation_controller)
):
    return await controller.get_diary_entry_recommendations(diary_entry_id, current_user)

@router.put("/{recommendation_id}", summary="Actualizar recomendación")
async def update_recommendation(
    recommendation_id: str = Path(...),
    dto: UpdateDiaryRecommendationDTO = ...,
    current_user: dict = Depends(get_current_user),
    controller: DiaryRecommendationController = Depends(get_recommendation_controller)
):
    return await controller.update_recommendation(recommendation_id, dto, current_user)

@router.delete("/{recommendation_id}", summary="Eliminar recomendación")
async def delete_recommendation(
    recommendation_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    controller: DiaryRecommendationController = Depends(get_recommendation_controller)
):
    return await controller.delete_recommendation(recommendation_id, current_user)