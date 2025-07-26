from fastapi import APIRouter, Depends, Query, Path
from typing import Optional
from ..controllers.diary_entry_controller import DiaryEntryController
from ...application.dtos.diary_entry_dto import (
    CreateDiaryEntryDTO, UpdateDiaryEntryDTO, AddEmotionDTO
)
from shared.middleware.AuthMiddleware import get_current_user
from shared.repositories.RepositoryFactory import RepositoryFactory
from shared.services.ServiceFactory import ServiceFactory
from shared.events.event_bus import EventBus

from ...application.use_cases.create_diary_entry import CreateDiaryEntryUseCase
from ...application.use_cases.get_diary_entry import GetDiaryEntryUseCase
from ...application.use_cases.get_day_diary_entries import GetDayDiaryEntriesUseCase
from ...application.use_cases.update_diary_entry import UpdateDiaryEntryUseCase
from ...application.use_cases.delete_diary_entry import DeleteDiaryEntryUseCase
from ...application.use_cases.add_emotion import AddEmotionUseCase
from ...application.use_cases.get_trip_diary_stats import GetTripDiaryStatsUseCase
from ...domain.diary_entry_service import DiaryEntryService

router = APIRouter()

def get_diary_entry_controller():
    diary_entry_repo = RepositoryFactory.get_diary_entry_repository()
    day_repo = RepositoryFactory.get_day_repository()
    trip_member_repo = RepositoryFactory.get_trip_member_repository()
    trip_repo = RepositoryFactory.get_trip_repository()
    user_repo = RepositoryFactory.get_user_repository()
    event_bus = EventBus()
    
    diary_entry_service = DiaryEntryService(
        diary_entry_repository=diary_entry_repo,
        day_repository=day_repo,
        trip_member_repository=trip_member_repo
    )
    
    create_diary_entry_use_case = CreateDiaryEntryUseCase(
        diary_entry_repository=diary_entry_repo,
        trip_member_repository=trip_member_repo,
        user_repository=user_repo,
        diary_entry_service=diary_entry_service,
        event_bus=event_bus
    )
    
    get_diary_entry_use_case = GetDiaryEntryUseCase(
        diary_entry_repository=diary_entry_repo,
        trip_member_repository=trip_member_repo,
        user_repository=user_repo,
        diary_entry_service=diary_entry_service
    )
    
    get_day_diary_entries_use_case = GetDayDiaryEntriesUseCase(
        diary_entry_repository=diary_entry_repo,
        day_repository=day_repo,
        trip_member_repository=trip_member_repo,
        user_repository=user_repo,
        diary_entry_service=diary_entry_service
    )
    
    update_diary_entry_use_case = UpdateDiaryEntryUseCase(
        diary_entry_repository=diary_entry_repo,
        trip_member_repository=trip_member_repo,
        user_repository=user_repo,
        diary_entry_service=diary_entry_service,
        event_bus=event_bus
    )
    
    delete_diary_entry_use_case = DeleteDiaryEntryUseCase(
        diary_entry_repository=diary_entry_repo,
        diary_entry_service=diary_entry_service,
        event_bus=event_bus
    )
    
    add_emotion_use_case = AddEmotionUseCase(
        diary_entry_repository=diary_entry_repo,
        user_repository=user_repo,
        diary_entry_service=diary_entry_service,
        event_bus=event_bus
    )
    
    get_trip_diary_stats_use_case = GetTripDiaryStatsUseCase(
        diary_entry_repository=diary_entry_repo,
        trip_repository=trip_repo,
        trip_member_repository=trip_member_repo,
        diary_entry_service=diary_entry_service
    )
    
    return DiaryEntryController(
        create_diary_entry_use_case=create_diary_entry_use_case,
        get_diary_entry_use_case=get_diary_entry_use_case,
        get_day_diary_entries_use_case=get_day_diary_entries_use_case,
        update_diary_entry_use_case=update_diary_entry_use_case,
        delete_diary_entry_use_case=delete_diary_entry_use_case,
        add_emotion_use_case=add_emotion_use_case,
        get_trip_diary_stats_use_case=get_trip_diary_stats_use_case
    )

# Rutas de entradas de diario
@router.post("/")
async def create_diary_entry(
    dto: CreateDiaryEntryDTO,
    current_user: dict = Depends(get_current_user),
    controller: DiaryEntryController = Depends(get_diary_entry_controller)
):
    return await controller.create_diary_entry(dto, current_user)

@router.get("/{entry_id}")
async def get_diary_entry(
    entry_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    controller: DiaryEntryController = Depends(get_diary_entry_controller)
):
    return await controller.get_diary_entry(entry_id, current_user)

@router.put("/{entry_id}")
async def update_diary_entry(
    entry_id: str = Path(...),
    dto: UpdateDiaryEntryDTO = None,
    current_user: dict = Depends(get_current_user),
    controller: DiaryEntryController = Depends(get_diary_entry_controller)
):
    return await controller.update_diary_entry(entry_id, dto, current_user)

@router.delete("/{entry_id}")
async def delete_diary_entry(
    entry_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    controller: DiaryEntryController = Depends(get_diary_entry_controller)
):
    return await controller.delete_diary_entry(entry_id, current_user)

@router.post("/{entry_id}/emotions")
async def add_emotion(
    entry_id: str = Path(...),
    dto: AddEmotionDTO = None,
    current_user: dict = Depends(get_current_user),
    controller: DiaryEntryController = Depends(get_diary_entry_controller)
):
    return await controller.add_emotion(entry_id, dto, current_user)

@router.get("/day/{day_id}")
async def get_day_diary_entries(
    day_id: str = Path(...),
    include_stats: bool = Query(True),
    current_user: dict = Depends(get_current_user),
    controller: DiaryEntryController = Depends(get_diary_entry_controller)
):
    return await controller.get_day_diary_entries(day_id, current_user, include_stats)

@router.get("/trip/{trip_id}/stats")
async def get_trip_diary_stats(
    trip_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    controller: DiaryEntryController = Depends(get_diary_entry_controller)
):
    return await controller.get_trip_diary_stats(trip_id, current_user)