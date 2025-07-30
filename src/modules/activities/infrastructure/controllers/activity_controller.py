# src/modules/activities/infrastructure/controllers/activity_controller.py
from fastapi import HTTPException
from typing import Optional

from ...application.dtos.activity_dto import (
    CreateActivityDTO, UpdateActivityDTO, ChangeActivityStatusDTO, ReorderActivitiesDTO,
    ActivityResponseDTO, DayActivitiesResponseDTO
)
from ...application.use_cases.create_activity import CreateActivityUseCase
from ...application.use_cases.get_activity import GetActivityUseCase
from ...application.use_cases.get_day_activities import GetDayActivitiesUseCase
from ...application.use_cases.update_activity import UpdateActivityUseCase
from ...application.use_cases.change_activity_status import ChangeActivityStatusUseCase
from ...application.use_cases.reorder_activities import ReorderActivitiesUseCase
from ...application.use_cases.delete_activity import DeleteActivityUseCase

from shared.utils.response_utils import SuccessResponse
from shared.errors.custom_errors import NotFoundError, ForbiddenError, ValidationError


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
        self._create_activity_use_case = create_activity_use_case
        self._get_activity_use_case = get_activity_use_case
        self._get_day_activities_use_case = get_day_activities_use_case
        self._update_activity_use_case = update_activity_use_case
        self._change_activity_status_use_case = change_activity_status_use_case
        self._reorder_activities_use_case = reorder_activities_use_case
        self._delete_activity_use_case = delete_activity_use_case

    async def create_activity(self, dto: CreateActivityDTO, current_user: dict) -> SuccessResponse:
        """Crear nueva actividad"""
        try:
            activity = await self._create_activity_use_case.execute(dto, current_user["id"])
            return SuccessResponse(
                message="Actividad creada exitosamente",
                data=activity
            )
        except (NotFoundError, ForbiddenError, ValidationError) as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    async def get_activity(self, activity_id: str, current_user: dict) -> SuccessResponse:
        """Obtener actividad por ID"""
        try:
            activity = await self._get_activity_use_case.execute(activity_id, current_user["id"])
            return SuccessResponse(
                message="Actividad obtenida exitosamente",
                data=activity
            )
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    async def get_day_activities(
        self, 
        day_id: str, 
        current_user: dict, 
        include_stats: bool = True
    ) -> SuccessResponse:
        """Obtener actividades de un día"""
        try:
            activities = await self._get_day_activities_use_case.execute(
                day_id, current_user["id"], include_stats
            )
            return SuccessResponse(
                message="Actividades obtenidas exitosamente",
                data=activities
            )
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    async def update_activity(
        self, 
        activity_id: str, 
        dto: UpdateActivityDTO, 
        current_user: dict
    ) -> SuccessResponse:
        """Actualizar actividad"""
        try:
            activity = await self._update_activity_use_case.execute(
                activity_id, dto, current_user["id"]
            )
            return SuccessResponse(
                message="Actividad actualizada exitosamente",
                data=activity
            )
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except (ForbiddenError, ValidationError) as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    async def change_activity_status(
        self, 
        activity_id: str, 
        dto: ChangeActivityStatusDTO, 
        current_user: dict
    ) -> SuccessResponse:
        """Cambiar estado de actividad"""
        try:
            activity = await self._change_activity_status_use_case.execute(
                activity_id, dto, current_user["id"]
            )
            return SuccessResponse(
                message="Estado de actividad actualizado exitosamente",
                data=activity
            )
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except (ForbiddenError, ValidationError) as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    async def reorder_activities(
        self, 
        day_id: str, 
        dto: ReorderActivitiesDTO, 
        current_user: dict
    ) -> SuccessResponse:
        """Reordenar actividades de un día"""
        try:
            activities = await self._reorder_activities_use_case.execute(
                day_id, dto, current_user["id"]
            )
            return SuccessResponse(
                message="Actividades reordenadas exitosamente",
                data=activities
            )
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except (ForbiddenError, ValidationError) as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    async def delete_activity(self, activity_id: str, current_user: dict) -> SuccessResponse:
        """Eliminar actividad"""
        try:
            success = await self._delete_activity_use_case.execute(activity_id, current_user["id"])
            if success:
                return SuccessResponse(
                    message="Actividad eliminada exitosamente",
                    data={"deleted": True}
                )
            else:
                raise HTTPException(status_code=400, detail="No se pudo eliminar la actividad")
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error interno del servidor")