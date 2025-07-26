from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import Annotated, Optional
from datetime import time

from ...application.dtos.activity_dto import (
    CreateActivityDTO, UpdateActivityDTO, ChangeActivityStatusDTO, ReorderActivitiesDTO,
    ActivityResponseDTO, DayActivitiesResponseDTO, ReorderResponseDTO
)
from ...application.use_cases.create_activity import CreateActivityUseCase
from ...application.use_cases.get_activity import GetActivityUseCase
from ...application.use_cases.get_day_activities import GetDayActivitiesUseCase
from ...application.use_cases.update_activity import UpdateActivityUseCase
from ...application.use_cases.change_activity_status import ChangeActivityStatusUseCase
from ...application.use_cases.reorder_activities import ReorderActivitiesUseCase
from ...application.use_cases.delete_activity import DeleteActivityUseCase

from shared.middleware.AuthMiddleware import get_current_user
from shared.utils.response_utils import SuccessResponse
from shared.utils.validation_utils import ValidationUtils


class ActivityController:
    def __init__(
        self,
        create_activity_use_case: CreateActivityUseCase,
        get_activity_use_case: GetActivityUseCase,
        get_day_activities_use_case: GetDayActivitiesUseCase,
        update_activity_use_case: UpdateActivityUseCase,
        change_activity_status_use_case: ChangeActivityStatusUseCase,
        reorder_activities_use_case: ReorderActivitiesUseCase,
        delete_activity_use_case: DeleteActivityUseCase
    ):
        self.router = APIRouter(prefix="/api/activities", tags=["actividades"])
        self._create_activity_use_case = create_activity_use_case
        self._get_activity_use_case = get_activity_use_case
        self._get_day_activities_use_case = get_day_activities_use_case
        self._update_activity_use_case = update_activity_use_case
        self._change_activity_status_use_case = change_activity_status_use_case
        self._reorder_activities_use_case = reorder_activities_use_case
        self._delete_activity_use_case = delete_activity_use_case
        
        self._setup_routes()

    def _setup_routes(self):
        self.router.add_api_route(
            "/",
            self.create_activity,
            methods=["POST"],
            response_model=SuccessResponse[ActivityResponseDTO]
        )
        self.router.add_api_route(
            "/{activity_id}",
            self.get_activity,
            methods=["GET"],
            response_model=SuccessResponse[ActivityResponseDTO]
        )
        self.router.add_api_route(
            "/{activity_id}",
            self.update_activity,
            methods=["PUT"],
            response_model=SuccessResponse[ActivityResponseDTO]
        )
        self.router.add_api_route(
            "/{activity_id}",
            self.delete_activity,
            methods=["DELETE"],
            response_model=SuccessResponse[bool]
        )
        self.router.add_api_route(
            "/{activity_id}/status",
            self.change_activity_status,
            methods=["PUT"],
            response_model=SuccessResponse[ActivityResponseDTO]
        )
        self.router.add_api_route(
            "/day/{day_id}",
            self.get_day_activities,
            methods=["GET"],
            response_model=SuccessResponse[DayActivitiesResponseDTO]
        )
        self.router.add_api_route(
            "/day/{day_id}/reorder",
            self.reorder_activities,
            methods=["PUT"],
            response_model=SuccessResponse[ReorderResponseDTO]
        )

    async def create_activity(
        self,
        dto: CreateActivityDTO,
        current_user: Annotated[dict, Depends(get_current_user)]
    ) -> SuccessResponse[ActivityResponseDTO]:
        """Crear nueva actividad"""
        try:
            validation_result = ValidationUtils.validate_uuid(dto.day_id)
            if not validation_result.is_valid:
                raise HTTPException(status_code=400, detail="ID de día inválido")

            result = await self._create_activity_use_case.execute(dto, current_user["sub"])
            
            return SuccessResponse(
                data=result,
                message="Actividad creada exitosamente"
            )
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    async def get_activity(
        self,
        activity_id: Annotated[str, Path()],
        current_user: Annotated[dict, Depends(get_current_user)]
    ) -> SuccessResponse[ActivityResponseDTO]:
        """Obtener actividad específica"""
        try:
            validation_result = ValidationUtils.validate_uuid(activity_id)
            if not validation_result.is_valid:
                raise HTTPException(status_code=400, detail="ID de actividad inválido")

            result = await self._get_activity_use_case.execute(activity_id, current_user["sub"])
            
            return SuccessResponse(data=result)
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    async def update_activity(
        self,
        activity_id: Annotated[str, Path()],
        dto: UpdateActivityDTO,
        current_user: Annotated[dict, Depends(get_current_user)]
    ) -> SuccessResponse[ActivityResponseDTO]:
        """Actualizar actividad existente"""
        try:
            validation_result = ValidationUtils.validate_uuid(activity_id)
            if not validation_result.is_valid:
                raise HTTPException(status_code=400, detail="ID de actividad inválido")

            result = await self._update_activity_use_case.execute(
                activity_id, dto, current_user["sub"]
            )
            
            return SuccessResponse(
                data=result,
                message="Actividad actualizada exitosamente"
            )
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    async def delete_activity(
        self,
        activity_id: Annotated[str, Path()],
        current_user: Annotated[dict, Depends(get_current_user)]
    ) -> SuccessResponse[bool]:
        """Eliminar actividad"""
        try:
            validation_result = ValidationUtils.validate_uuid(activity_id)
            if not validation_result.is_valid:
                raise HTTPException(status_code=400, detail="ID de actividad inválido")

            result = await self._delete_activity_use_case.execute(activity_id, current_user["sub"])
            
            return SuccessResponse(
                data=result,
                message="Actividad eliminada exitosamente"
            )
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    async def change_activity_status(
        self,
        activity_id: Annotated[str, Path()],
        dto: ChangeActivityStatusDTO,
        current_user: Annotated[dict, Depends(get_current_user)]
    ) -> SuccessResponse[ActivityResponseDTO]:
        """Cambiar estado de actividad"""
        try:
            validation_result = ValidationUtils.validate_uuid(activity_id)
            if not validation_result.is_valid:
                raise HTTPException(status_code=400, detail="ID de actividad inválido")

            result = await self._change_activity_status_use_case.execute(
                activity_id, dto, current_user["sub"]
            )
            
            return SuccessResponse(
                data=result,
                message="Estado de actividad actualizado exitosamente"
            )
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    async def get_day_activities(
        self,
        day_id: Annotated[str, Path()],
        current_user: Annotated[dict, Depends(get_current_user)]
    ) -> SuccessResponse[DayActivitiesResponseDTO]:
        """Obtener todas las actividades de un día"""
        try:
            validation_result = ValidationUtils.validate_uuid(day_id)
            if not validation_result.is_valid:
                raise HTTPException(status_code=400, detail="ID de día inválido")

            result = await self._get_day_activities_use_case.execute(day_id, current_user["sub"])
            
            return SuccessResponse(
                data=result,
                message="Actividades obtenidas exitosamente"
            )
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    async def reorder_activities(
        self,
        day_id: Annotated[str, Path()],
        dto: ReorderActivitiesDTO,
        current_user: Annotated[dict, Depends(get_current_user)]
    ) -> SuccessResponse[ReorderResponseDTO]:
        """Reordenar actividades de un día"""
        try:
            validation_result = ValidationUtils.validate_uuid(day_id)
            if not validation_result.is_valid:
                raise HTTPException(status_code=400, detail="ID de día inválido")

            # Asegurar que el day_id del DTO coincida con el path
            dto.day_id = day_id

            result = await self._reorder_activities_use_case.execute(dto, current_user["sub"])
            
            return SuccessResponse(
                data=result,
                message="Actividades reordenadas exitosamente"
            )
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error interno del servidor")