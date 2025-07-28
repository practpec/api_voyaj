# ====================================
# 1. src/modules/days/infrastructure/routes/day_routes.py
# ====================================
from fastapi import APIRouter, Depends, Path
from ..controllers.day_controller import DayController
from ...application.dtos.day_dto import CreateDayDTO, UpdateDayDTO
from shared.middleware.AuthMiddleware import get_current_user
from shared.repositories.RepositoryFactory import RepositoryFactory
from shared.events.event_bus import EventBus

from ...application.use_cases.create_day import CreateDayUseCase
from ...application.use_cases.get_day import GetDayUseCase
from ...application.use_cases.get_trip_days import GetTripDaysUseCase
from ...application.use_cases.update_day import UpdateDayUseCase
from ...application.use_cases.delete_day import DeleteDayUseCase
from ...application.use_cases.generate_trip_days import GenerateTripDaysUseCase
from ...domain.day_service import DayService

router = APIRouter()

def get_day_controller():
    """Factory para crear controlador de days con dependencias"""
    try:
        day_repo = RepositoryFactory.get_day_repository()
        trip_repo = RepositoryFactory.get_trip_repository()
        trip_member_repo = RepositoryFactory.get_trip_member_repository()
        event_bus = EventBus.get_instance()
        
        day_service = DayService(day_repo, trip_repo, trip_member_repo)
        
        return DayController(
            create_day_use_case=CreateDayUseCase(
                day_repo, trip_member_repo, day_service, event_bus
            ),
            get_day_use_case=GetDayUseCase(
                day_repo, trip_member_repo, day_service
            ),
            get_trip_days_use_case=GetTripDaysUseCase(
                day_repo, day_service
            ),
            update_day_use_case=UpdateDayUseCase(
                day_repo, trip_member_repo, day_service, event_bus
            ),
            delete_day_use_case=DeleteDayUseCase(
                day_repo, day_service, event_bus
            ),
            generate_trip_days_use_case=GenerateTripDaysUseCase(
                day_repo, trip_member_repo, day_service, event_bus
            )
        )
    except Exception as e:
        print(f"[ERROR] Error creando day controller: {str(e)}")
        raise Exception(f"Error inicializando controlador de días: {str(e)}")

@router.post("/")
async def create_day(
    dto: CreateDayDTO,
    current_user: dict = Depends(get_current_user),
    controller: DayController = Depends(get_day_controller)
):
    """Crear nuevo día en un viaje"""
    return await controller.create_day(dto, current_user)

@router.get("/{day_id}")
async def get_day(
    day_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    controller: DayController = Depends(get_day_controller)
):
    """Obtener día específico"""
    return await controller.get_day(day_id, current_user)

@router.put("/{day_id}")
async def update_day(
    day_id: str = Path(...),
    dto: UpdateDayDTO = None,
    current_user: dict = Depends(get_current_user),
    controller: DayController = Depends(get_day_controller)
):
    """Actualizar día existente"""
    return await controller.update_day(day_id, dto, current_user)

@router.delete("/{day_id}")
async def delete_day(
    day_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    controller: DayController = Depends(get_day_controller)
):
    """Eliminar día"""
    return await controller.delete_day(day_id, current_user)

@router.get("/trip/{trip_id}/timeline")
async def get_trip_timeline(
    trip_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    controller: DayController = Depends(get_day_controller)
):
    """Obtener timeline de días del viaje"""
    return await controller.get_trip_timeline(trip_id, current_user)

@router.post("/trip/{trip_id}/generate")
async def generate_trip_days(
    trip_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    controller: DayController = Depends(get_day_controller)
):
    """Generar automáticamente todos los días del viaje"""
    return await controller.generate_trip_days(trip_id, current_user)