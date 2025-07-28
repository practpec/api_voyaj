from fastapi import HTTPException
from typing import Optional

from ...application.dtos.trip_dto import (
    CreateTripDTO, UpdateTripDTO, UpdateTripStatusDTO, TripFiltersDTO,
    TripResponseDTO, TripListResponseDTO, TripStatsDTO
)
from ...application.dtos.trip_member_dto import (
    InviteMemberDTO, TripMemberResponseDTO, TripMemberListResponseDTO,
    HandleInvitationDTO
)
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

from shared.utils.response_utils import SuccessResponse, PaginatedResponse
from shared.utils.validation_utils import ValidationUtils
from shared.errors.custom_errors import NotFoundError, ValidationError, ForbiddenError


class TripController:
    def __init__(
        self,
        create_trip_use_case: CreateTripUseCase,
        get_trip_use_case: GetTripUseCase,
        get_user_trips_use_case: GetUserTripsUseCase,
        update_trip_use_case: UpdateTripUseCase,
        delete_trip_use_case: DeleteTripUseCase,
        update_trip_status_use_case: UpdateTripStatusUseCase,
        invite_user_to_trip_use_case: InviteUserToTripUseCase,
        handle_trip_invitation_use_case: HandleTripInvitationUseCase,
        get_trip_members_use_case: GetTripMembersUseCase,
        leave_trip_use_case: LeaveTripUseCase,
        remove_trip_member_use_case: RemoveTripMemberUseCase,
        update_member_role_use_case: UpdateMemberRoleUseCase
    ):
        self._create_trip_use_case = create_trip_use_case
        self._get_trip_use_case = get_trip_use_case
        self._get_user_trips_use_case = get_user_trips_use_case
        self._update_trip_use_case = update_trip_use_case
        self._delete_trip_use_case = delete_trip_use_case
        self._update_trip_status_use_case = update_trip_status_use_case
        self._invite_user_to_trip_use_case = invite_user_to_trip_use_case
        self._handle_trip_invitation_use_case = handle_trip_invitation_use_case
        self._get_trip_members_use_case = get_trip_members_use_case
        self._leave_trip_use_case = leave_trip_use_case
        self._remove_trip_member_use_case = remove_trip_member_use_case
        self._update_member_role_use_case = update_member_role_use_case

    async def get_user_trips(
        self,
        current_user: dict,
        status: Optional[str] = None,
        category: Optional[str] = None,
        is_group_trip: Optional[bool] = None,
        destination: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> PaginatedResponse[TripListResponseDTO]:
        """Obtener viajes del usuario con filtros"""
        try:
            filters = TripFiltersDTO(
                status=status,
                category=category,
                is_group_trip=is_group_trip,
                destination=destination,
                limit=limit,
                offset=offset
            )
            
            result = await self._get_user_trips_use_case.execute(
                current_user["sub"],
                filters
            )
            return result
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def create_trip(
        self,
        dto: CreateTripDTO,
        current_user: dict
    ) -> SuccessResponse[TripResponseDTO]:
        """Crear nuevo viaje"""
        try:
            result = await self._create_trip_use_case.execute(dto, current_user["sub"])
            
            
            return SuccessResponse(
                data=result,
                message="Viaje creado exitosamente"
            )
            
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def get_trip(
        self,
        trip_id: str,
        current_user: dict
    ) -> SuccessResponse[TripResponseDTO]:
        """Obtener detalles de un viaje"""
        try:
            validation_result = ValidationUtils.validate_uuid(trip_id)
            if not validation_result.is_valid:
                raise HTTPException(status_code=400, detail="ID de viaje inválido")

            result = await self._get_trip_use_case.execute(trip_id, current_user["sub"])
            
            return SuccessResponse(
                data=result,
                message="Viaje obtenido exitosamente"
            )
            
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def update_trip(
        self,
        trip_id: str,
        dto: UpdateTripDTO,
        current_user: dict
    ) -> SuccessResponse[TripResponseDTO]:
        """Actualizar viaje"""
        try:
            validation_result = ValidationUtils.validate_uuid(trip_id)
            if not validation_result.is_valid:
                raise HTTPException(status_code=400, detail="ID de viaje inválido")

            result = await self._update_trip_use_case.execute(trip_id, dto, current_user["sub"])
            
            return SuccessResponse(
                data=result,
                message="Viaje actualizado exitosamente"
            )
            
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def delete_trip(
        self,
        trip_id: str,
        current_user: dict
    ) -> SuccessResponse[bool]:
        """Eliminar viaje"""
        try:
            validation_result = ValidationUtils.validate_uuid(trip_id)
            if not validation_result.is_valid:
                raise HTTPException(status_code=400, detail="ID de viaje inválido")

            await self._delete_trip_use_case.execute(trip_id, current_user["sub"])
            
            return SuccessResponse(
                data=True,
                message="Viaje eliminado exitosamente"
            )
            
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def update_trip_status(
        self,
        trip_id: str,
        dto: UpdateTripStatusDTO,
        current_user: dict
    ) -> SuccessResponse[TripResponseDTO]:
        """Actualizar estado del viaje"""
        try:
            validation_result = ValidationUtils.validate_uuid(trip_id)
            if not validation_result.is_valid:
                raise HTTPException(status_code=400, detail="ID de viaje inválido")

            result = await self._update_trip_status_use_case.execute(trip_id, dto, current_user["sub"])
            
            return SuccessResponse(
                data=result,
                message="Estado del viaje actualizado exitosamente"
            )
            
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def get_trip_members(
        self,
        trip_id: str,
        current_user: dict,
        limit: int = 20,
        offset: int = 0
    ) -> PaginatedResponse[TripMemberListResponseDTO]:
        """Obtener miembros del viaje"""
        try:
            validation_result = ValidationUtils.validate_uuid(trip_id)
            if not validation_result.is_valid:
                raise HTTPException(status_code=400, detail="ID de viaje inválido")

            # Importar aquí para evitar problemas de dependencias circulares
            from ...application.dtos.trip_member_dto import TripMemberFiltersDTO
            
            # Crear filtros DTO con limit y offset
            filters = TripMemberFiltersDTO(
                limit=limit,
                offset=offset
            )

            result = await self._get_trip_members_use_case.execute(
                trip_id, current_user["sub"], filters
            )
            
            return result
            
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def invite_member(
        self,
        trip_id: str,
        dto: InviteMemberDTO,
        current_user: dict
    ) -> SuccessResponse[TripMemberResponseDTO]:
        """Invitar usuario al viaje"""
        try:
            validation_result = ValidationUtils.validate_uuid(trip_id)
            if not validation_result.is_valid:
                raise HTTPException(status_code=400, detail="ID de viaje inválido")

            result = await self._invite_user_to_trip_use_case.execute(
                trip_id, dto, current_user["sub"]
            )
            
            return SuccessResponse(
                data=result,
                message="Invitación enviada exitosamente"
            )
            
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def accept_invitation(
        self,
        trip_id: str,
        member_id: str,
        current_user: dict
    ) -> SuccessResponse[TripMemberResponseDTO]:
        """Aceptar invitación al viaje"""
        try:
            validation_result = ValidationUtils.validate_uuid(trip_id)
            if not validation_result.is_valid:
                raise HTTPException(status_code=400, detail="ID de viaje inválido")

            from ...application.dtos.trip_member_dto import HandleInvitationDTO
            dto = HandleInvitationDTO(action="accept")
            
            # El caso de uso maneja la invitación del usuario actual, no necesita member_id
            result = await self._handle_trip_invitation_use_case.execute(
                trip_id, dto, current_user["sub"]
            )
            
            return SuccessResponse(
                data=result,
                message="Invitación aceptada exitosamente"
            )
            
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def reject_invitation(
        self,
        trip_id: str,
        member_id: str,
        current_user: dict
    ) -> SuccessResponse[bool]:
        """Rechazar invitación al viaje"""
        try:
            validation_result = ValidationUtils.validate_uuid(trip_id)
            if not validation_result.is_valid:
                raise HTTPException(status_code=400, detail="ID de viaje inválido")

            from ...application.dtos.trip_member_dto import HandleInvitationDTO
            dto = HandleInvitationDTO(action="reject")
            
            # El caso de uso maneja la invitación del usuario actual, no necesita member_id
            await self._handle_trip_invitation_use_case.execute(
                trip_id, dto, current_user["sub"]
            )
            
            return SuccessResponse(
                data=True,
                message="Invitación rechazada exitosamente"
            )
            
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def leave_trip(
        self,
        trip_id: str,
        current_user: dict
    ) -> SuccessResponse[bool]:
        """Abandonar viaje"""
        try:
            validation_result = ValidationUtils.validate_uuid(trip_id)
            if not validation_result.is_valid:
                raise HTTPException(status_code=400, detail="ID de viaje inválido")

            await self._leave_trip_use_case.execute(trip_id, current_user["sub"])
            
            return SuccessResponse(
                data=True,
                message="Has abandonado el viaje exitosamente"
            )
            
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def remove_member(
        self,
        trip_id: str,
        member_id: str,
        current_user: dict
    ) -> SuccessResponse[bool]:
        """Remover miembro del viaje"""
        try:
            validation_result = ValidationUtils.validate_uuid(trip_id)
            if not validation_result.is_valid:
                raise HTTPException(status_code=400, detail="ID de viaje inválido")
                
            member_validation = ValidationUtils.validate_uuid(member_id)
            if not member_validation.is_valid:
                raise HTTPException(status_code=400, detail="ID de miembro inválido")

            await self._remove_trip_member_use_case.execute(
                trip_id, member_id, current_user["sub"]
            )
            
            return SuccessResponse(
                data=True,
                message="Miembro removido del viaje exitosamente"
            )
            
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def update_member_role(
        self,
        trip_id: str,
        member_id: str,
        new_role: str,
        current_user: dict
    ) -> SuccessResponse[TripMemberResponseDTO]:
        """Actualizar rol de miembro"""
        try:
            validation_result = ValidationUtils.validate_uuid(trip_id)
            if not validation_result.is_valid:
                raise HTTPException(status_code=400, detail="ID de viaje inválido")
                
            member_validation = ValidationUtils.validate_uuid(member_id)
            if not member_validation.is_valid:
                raise HTTPException(status_code=400, detail="ID de miembro inválido")

            result = await self._update_member_role_use_case.execute(
                trip_id, member_id, new_role, current_user["sub"]
            )
            
            return SuccessResponse(
                data=result,
                message="Rol actualizado exitosamente"
            )
            
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def health_check(self) -> SuccessResponse:
        """Health check del módulo trips"""
        return SuccessResponse(
            message="Módulo trips funcionando correctamente",
            data={
                "status": "healthy",
                "module": "trips",
                "features": [
                    "create_trip", "get_trip", "update_trip", "delete_trip",
                    "trip_status", "trip_members", "invitations"
                ]
            }
        )