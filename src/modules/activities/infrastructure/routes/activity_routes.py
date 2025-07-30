# src/modules/activities/infrastructure/routes/activity_routes.py
from fastapi import APIRouter, Depends, Query, Path
from typing import Optional
from ..controllers.activity_controller import ActivityController
from ...application.dtos.activity_dto import (
    CreateActivityDTO, UpdateActivityDTO, ChangeActivityStatusDTO, ReorderActivitiesDTO
)
from shared.middleware.AuthMiddleware import get_current_user
from shared.repositories.RepositoryFactory import RepositoryFactory
from shared.services.ServiceFactory import ServiceFactory
from shared.events.event_bus import EventBus

from ...application.use_cases.create_activity import CreateActivityUseCase
from ...application.use_cases.get_activity import GetActivityUseCase
from ...application.use_cases.get_day_activities import GetDayActivitiesUseCase
from ...application.use_cases.update_activity import UpdateActivityUseCase
from ...application.use_cases.change_activity_status import ChangeActivityStatusUseCase
from ...application.use_cases.reorder_activities import ReorderActivitiesUseCase
from ...application.use_cases.delete_activity import DeleteActivityUseCase

router = APIRouter()

def get_activity_controller():
    activity_repo = RepositoryFactory.get_activity_repository()
    trip_member_repo = RepositoryFactory.get_trip_member_repository()
    user_repo = RepositoryFactory.get_user_repository()
    day_repo = RepositoryFactory.get_day_repository()
    event_bus = EventBus.get_instance()
    
    activity_service = ServiceFactory.get_activity_service()
    
    create_activity_use_case = CreateActivityUseCase(
        activity_repository=activity_repo,
        trip_member_repository=trip_member_repo,
        user_repository=user_repo,
        day_repository=day_repo,
        activity_service=activity_service,
        event_bus=event_bus
    )
    
    get_activity_use_case = GetActivityUseCase(
        activity_repository=activity_repo,
        day_repository=day_repo,
        trip_member_repository=trip_member_repo,
        activity_service=activity_service
    )
    
    get_day_activities_use_case = GetDayActivitiesUseCase(
        activity_repository=activity_repo,
        day_repository=day_repo,
        trip_member_repository=trip_member_repo,
        activity_service=activity_service
    )
    
    update_activity_use_case = UpdateActivityUseCase(
        activity_repository=activity_repo,
        trip_member_repository=trip_member_repo,
        user_repository=user_repo,
        activity_service=activity_service,
        event_bus=event_bus
    )
    
    change_activity_status_use_case = ChangeActivityStatusUseCase(
        activity_repository=activity_repo,
        trip_member_repository=trip_member_repo,
        user_repository=user_repo,
        activity_service=activity_service,
        event_bus=event_bus
    )
    
    reorder_activities_use_case = ReorderActivitiesUseCase(
        activity_repository=activity_repo,
        day_repository=day_repo,
        trip_member_repository=trip_member_repo,
        activity_service=activity_service,
        event_bus=event_bus
    )
    
    delete_activity_use_case = DeleteActivityUseCase(
        activity_repository=activity_repo,
        trip_member_repository=trip_member_repo,
        activity_service=activity_service,
        event_bus=event_bus
    )
    
    return ActivityController(
        create_activity_use_case=create_activity_use_case,
        get_activity_use_case=get_activity_use_case,
        get_day_activities_use_case=get_day_activities_use_case,
        update_activity_use_case=update_activity_use_case,
        change_activity_status_use_case=change_activity_status_use_case,
        reorder_activities_use_case=reorder_activities_use_case,
        delete_activity_use_case=delete_activity_use_case
    )

# Rutas de actividades
@router.post("/")
async def create_activity(
    dto: CreateActivityDTO,
    current_user: dict = Depends(get_current_user),
    controller: ActivityController = Depends(get_activity_controller)
):
    return await controller.create_activity(dto, current_user)

@router.get("/{activity_id}")
async def get_activity(
    activity_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    controller: ActivityController = Depends(get_activity_controller)
):
    return await controller.get_activity(activity_id, current_user)

@router.put("/{activity_id}")
async def update_activity(
    activity_id: str = Path(...),
    dto: UpdateActivityDTO = None,
    current_user: dict = Depends(get_current_user),
    controller: ActivityController = Depends(get_activity_controller)
):
    return await controller.update_activity(activity_id, dto, current_user)

@router.delete("/{activity_id}")
async def delete_activity(
    activity_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    controller: ActivityController = Depends(get_activity_controller)
):
    return await controller.delete_activity(activity_id, current_user)

@router.put("/{activity_id}/status")
async def change_activity_status(
    activity_id: str = Path(...),
    dto: ChangeActivityStatusDTO = None,
    current_user: dict = Depends(get_current_user),
    controller: ActivityController = Depends(get_activity_controller)
):
    return await controller.change_activity_status(activity_id, dto, current_user)

@router.get("/day/{day_id}")
async def get_day_activities(
    day_id: str = Path(...),
    include_stats: bool = Query(True),
    current_user: dict = Depends(get_current_user),
    controller: ActivityController = Depends(get_activity_controller)
):
    return await controller.get_day_activities(day_id, current_user, include_stats)

@router.put("/day/{day_id}/reorder")
async def reorder_activities(
    day_id: str = Path(...),
    dto: ReorderActivitiesDTO = None,
    current_user: dict = Depends(get_current_user),
    controller: ActivityController = Depends(get_activity_controller)
):
    return await controller.reorder_activities(day_id, dto, current_user)