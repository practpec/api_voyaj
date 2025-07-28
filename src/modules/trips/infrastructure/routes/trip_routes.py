# src/modules/trips/infrastructure/routes/trip_routes.py
from fastapi import APIRouter, Depends, Query, Path, Body
from typing import Optional
from ..controllers.trip_controller import TripController
from ...application.dtos.trip_dto import (
    CreateTripDTO, UpdateTripDTO, UpdateTripStatusDTO
)
from ...application.dtos.trip_member_dto import InviteMemberDTO, HandleInvitationDTO
from shared.middleware.AuthMiddleware import get_current_user
from shared.repositories.RepositoryFactory import RepositoryFactory
from shared.services.ServiceFactory import ServiceFactory
from shared.events.event_bus import EventBus

from ...application.use_cases.create_trip import CreateTripUseCase
from ...application.use_cases.get_trip import GetTripUseCase
from ...application.use_cases.get_user_trips import GetUserTripsUseCase
from ...application.use_cases.update_trip import UpdateTripUseCase
from ...application.use_cases.delete_trip import DeleteTripUseCase
from ...application.use_cases.update_trip_status import UpdateTripStatusUseCase
from ...application.use_cases.invite_user_to_trip import InviteUserToTripUseCase
from ...application.use_cases.handle_trip_invitation import HandleTripInvitationUseCase
from ...application.use_cases.get_trip_members import GetTripMembersUseCase
from ...application.use_cases.leave_trip import LeaveTripUseCase
from ...application.use_cases.remove_trip_member import RemoveTripMemberUseCase
from ...application.use_cases.update_member_role import UpdateMemberRoleUseCase

router = APIRouter()

def get_trip_controller():
    """Factory para crear controlador de trips con dependencias"""
    trip_repo = RepositoryFactory.get_trip_repository()
    trip_member_repo = RepositoryFactory.get_trip_member_repository()
    user_repo = RepositoryFactory.get_user_repository()
    trip_service = ServiceFactory.get_trip_service()
    event_bus = EventBus.get_instance()
    
    return TripController(
        create_trip_use_case=CreateTripUseCase(
            trip_repo, trip_member_repo, user_repo, trip_service, event_bus
        ),
        get_trip_use_case=GetTripUseCase(
            trip_repo, trip_member_repo, user_repo, trip_service
        ),
        get_user_trips_use_case=GetUserTripsUseCase(
            trip_repo, trip_member_repo, trip_service
        ),
        update_trip_use_case=UpdateTripUseCase(
            trip_repo, trip_member_repo, user_repo, trip_service, event_bus
        ),
        delete_trip_use_case=DeleteTripUseCase(
            trip_repo, trip_member_repo, trip_service, event_bus
        ),
        update_trip_status_use_case=UpdateTripStatusUseCase(
            trip_repo, trip_member_repo, user_repo, trip_service, event_bus
        ),
        invite_user_to_trip_use_case=InviteUserToTripUseCase(
            trip_repo, trip_member_repo, user_repo, trip_service, event_bus
        ),
        handle_trip_invitation_use_case=HandleTripInvitationUseCase(
            trip_repo, trip_member_repo, user_repo, trip_service, event_bus
        ),
        get_trip_members_use_case=GetTripMembersUseCase(
            trip_member_repo, user_repo, trip_service
        ),
        leave_trip_use_case=LeaveTripUseCase(
            trip_repo, trip_member_repo, user_repo, trip_service, event_bus
        ),
        remove_trip_member_use_case=RemoveTripMemberUseCase(
            trip_repo, trip_member_repo, user_repo, trip_service, event_bus
        ),
        update_member_role_use_case=UpdateMemberRoleUseCase(
            trip_repo, trip_member_repo, user_repo, trip_service, event_bus
        )
    )

# =====================================================
# ENDPOINTS PRINCIPALES DE VIAJES
# =====================================================

@router.get("/")
async def get_user_trips(
    status: Optional[str] = Query(None, description="Filtro por estado del viaje"),
    category: Optional[str] = Query(None, description="Filtro por categoría"),
    is_group_trip: Optional[bool] = Query(None, description="Filtro por tipo de viaje"),
    destination: Optional[str] = Query(None, description="Filtro por destino"),
    limit: int = Query(20, ge=1, le=100, description="Número de resultados"),
    offset: int = Query(0, ge=0, description="Desplazamiento para paginación"),
    current_user: dict = Depends(get_current_user),
    controller: TripController = Depends(get_trip_controller)
):
    """Obtener viajes del usuario autenticado con filtros opcionales"""
    return await controller.get_user_trips(
        current_user, status, category, is_group_trip, destination, limit, offset
    )

@router.post("/")
async def create_trip(
    dto: CreateTripDTO,
    current_user: dict = Depends(get_current_user),
    controller: TripController = Depends(get_trip_controller)
):
    """Crear nuevo viaje"""
    return await controller.create_trip(dto, current_user)

@router.get("/{trip_id}")
async def get_trip(
    trip_id: str = Path(..., description="ID único del viaje"),
    current_user: dict = Depends(get_current_user),
    controller: TripController = Depends(get_trip_controller)
):
    """Obtener detalles completos de un viaje específico"""
    return await controller.get_trip(trip_id, current_user)

@router.put("/{trip_id}")
async def update_trip(
    dto: UpdateTripDTO,
    trip_id: str = Path(..., description="ID único del viaje"),
    current_user: dict = Depends(get_current_user),
    controller: TripController = Depends(get_trip_controller)
):
    """Actualizar información del viaje"""
    return await controller.update_trip(trip_id, dto, current_user)

@router.delete("/{trip_id}")
async def delete_trip(
    trip_id: str = Path(..., description="ID único del viaje"),
    current_user: dict = Depends(get_current_user),
    controller: TripController = Depends(get_trip_controller)
):
    """Eliminar viaje (soft delete)"""
    return await controller.delete_trip(trip_id, current_user)

@router.put("/{trip_id}/status")
async def update_trip_status(
    dto: UpdateTripStatusDTO,
    trip_id: str = Path(..., description="ID único del viaje"),
    current_user: dict = Depends(get_current_user),
    controller: TripController = Depends(get_trip_controller)
):
    """Actualizar estado del viaje (planificado, activo, completado, cancelado)"""
    return await controller.update_trip_status(trip_id, dto, current_user)

# =====================================================
# ENDPOINTS DE MIEMBROS DEL VIAJE
# =====================================================

@router.get("/{trip_id}/members")
async def get_trip_members(
    trip_id: str = Path(..., description="ID único del viaje"),
    limit: int = Query(20, ge=1, le=100, description="Número de resultados"),
    offset: int = Query(0, ge=0, description="Desplazamiento para paginación"),
    current_user: dict = Depends(get_current_user),
    controller: TripController = Depends(get_trip_controller)
):
    """Obtener lista de miembros del viaje"""
    return await controller.get_trip_members(trip_id, current_user, limit, offset)

@router.post("/{trip_id}/members")
async def invite_member(
    dto: InviteMemberDTO,
    trip_id: str = Path(..., description="ID único del viaje"),
    current_user: dict = Depends(get_current_user),
    controller: TripController = Depends(get_trip_controller)
):
    """Invitar usuario al viaje"""
    return await controller.invite_member(trip_id, dto, current_user)

# =====================================================
# ENDPOINTS DE INVITACIONES (FIXED)
# =====================================================

@router.post("/{trip_id}/members/{invitation_id}/accept")
async def accept_invitation(
    trip_id: str = Path(..., description="ID único del viaje"),
    invitation_id: str = Path(..., description="ID de la invitación"),
    current_user: dict = Depends(get_current_user),
    controller: TripController = Depends(get_trip_controller)
):
    """
    Aceptar invitación al viaje.
    
    El usuario actual acepta su invitación pendiente para el viaje especificado.
    El invitation_id puede ser cualquier valor válido, internamente se busca 
    la invitación del usuario actual.
    """
    return await controller.accept_invitation(trip_id, invitation_id, current_user)

@router.post("/{trip_id}/members/{invitation_id}/reject")
async def reject_invitation(
    trip_id: str = Path(..., description="ID único del viaje"),
    invitation_id: str = Path(..., description="ID de la invitación"),
    current_user: dict = Depends(get_current_user),
    controller: TripController = Depends(get_trip_controller)
):
    """
    Rechazar invitación al viaje.
    
    El usuario actual rechaza su invitación pendiente para el viaje especificado.
    El invitation_id puede ser cualquier valor válido, internamente se busca 
    la invitación del usuario actual.
    """
    return await controller.reject_invitation(trip_id, invitation_id, current_user)

# =====================================================
# ENDPOINTS ADICIONALES DE GESTIÓN DE MIEMBROS
# =====================================================

@router.post("/{trip_id}/leave")
async def leave_trip(
    trip_id: str = Path(..., description="ID único del viaje"),
    current_user: dict = Depends(get_current_user),
    controller: TripController = Depends(get_trip_controller)
):
    """Abandonar el viaje"""
    return await controller.leave_trip(trip_id, current_user)

@router.delete("/{trip_id}/members/{member_id}")
async def remove_member(
    trip_id: str = Path(..., description="ID único del viaje"),
    member_id: str = Path(..., description="ID único del miembro"),
    current_user: dict = Depends(get_current_user),
    controller: TripController = Depends(get_trip_controller)
):
    """Remover miembro del viaje (solo admins/owners)"""
    return await controller.remove_member(trip_id, member_id, current_user)

@router.put("/{trip_id}/members/{member_id}/role")
async def update_member_role(
    trip_id: str = Path(..., description="ID único del viaje"),
    member_id: str = Path(..., description="ID único del miembro"),
    new_role: str = Query(..., description="Nuevo rol del miembro"),
    current_user: dict = Depends(get_current_user),
    controller: TripController = Depends(get_trip_controller)
):
    """Actualizar rol de miembro (owner, admin, member)"""
    return await controller.update_member_role(trip_id, member_id, new_role, current_user)

# =====================================================
# ENDPOINT DE HEALTH CHECK
# =====================================================

@router.get("/health")
async def health_check(
    controller: TripController = Depends(get_trip_controller)
):
    """Health check del módulo trips"""
    return await controller.health_check()