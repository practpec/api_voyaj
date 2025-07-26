from fastapi import APIRouter, Depends, Path
from typing import Annotated

from ...application.dtos.plan_reality_difference_dto import (
    CreatePlanRealityDifferenceDTO, 
    UpdatePlanRealityDifferenceDTO
)
from ...application.use_cases.create_plan_reality_difference import CreatePlanRealityDifferenceUseCase
from ...application.use_cases.get_plan_reality_difference import GetPlanRealityDifferenceUseCase
from ...application.use_cases.get_trip_differences import GetTripDifferencesUseCase
from ...application.use_cases.get_trip_analysis import GetTripAnalysisUseCase
from ...infrastructure.controllers.plan_reality_difference_controller import PlanRealityDifferenceController

from shared.middleware.AuthMiddleware import get_current_user
from shared.repositories.RepositoryFactory import RepositoryFactory
from shared.services.ServiceFactory import ServiceFactory

router = APIRouter()

def get_plan_reality_difference_controller() -> PlanRealityDifferenceController:
    """Factory para crear controlador de diferencias plan vs realidad"""
    
    # Repositorios y servicios desde factory
    plan_reality_difference_repo = RepositoryFactory.get_plan_reality_difference_repository()
    plan_reality_difference_service = ServiceFactory.get_plan_reality_difference_service()
    
    # Use cases
    create_difference_use_case = CreatePlanRealityDifferenceUseCase(
        plan_reality_difference_repository=plan_reality_difference_repo,
        plan_reality_difference_service=plan_reality_difference_service
    )
    
    get_difference_use_case = GetPlanRealityDifferenceUseCase(
        plan_reality_difference_repository=plan_reality_difference_repo,
        plan_reality_difference_service=plan_reality_difference_service
    )
    
    get_trip_differences_use_case = GetTripDifferencesUseCase(
        plan_reality_difference_repository=plan_reality_difference_repo,
        plan_reality_difference_service=plan_reality_difference_service
    )
    
    get_trip_analysis_use_case = GetTripAnalysisUseCase(
        plan_reality_difference_service=plan_reality_difference_service
    )
    
    return PlanRealityDifferenceController(
        create_difference_use_case=create_difference_use_case,
        get_difference_use_case=get_difference_use_case,
        get_trip_differences_use_case=get_trip_differences_use_case,
        get_trip_analysis_use_case=get_trip_analysis_use_case
    )

# Rutas principales de diferencias
@router.post("/")
async def create_difference(
    dto: CreatePlanRealityDifferenceDTO,
    current_user: dict = Depends(get_current_user),
    controller: PlanRealityDifferenceController = Depends(get_plan_reality_difference_controller)
):
    return await controller.create_difference(dto, current_user)

@router.get("/{difference_id}")
async def get_difference(
    difference_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    controller: PlanRealityDifferenceController = Depends(get_plan_reality_difference_controller)
):
    return await controller.get_difference(difference_id, current_user)

# Rutas de viaje
@router.get("/trip/{trip_id}")
async def get_trip_differences(
    trip_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    controller: PlanRealityDifferenceController = Depends(get_plan_reality_difference_controller)
):
    return await controller.get_trip_differences(trip_id, current_user)

@router.get("/trip/{trip_id}/analysis")
async def get_trip_analysis(
    trip_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    controller: PlanRealityDifferenceController = Depends(get_plan_reality_difference_controller)
):
    return await controller.get_trip_analysis(trip_id, current_user)

# Health check
@router.get("/health")
async def health_check(
    controller: PlanRealityDifferenceController = Depends(get_plan_reality_difference_controller)
):
    return await controller.health_check()