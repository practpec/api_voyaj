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

    async def create_activity(self, dto: CreateActivityDTO, current_user: dict):
           """Crear nueva actividad"""
           try:
               # CORREGIDO: Extraer el ID del usuario del token
               user_id = current_user.get("sub") if isinstance(current_user, dict) else current_user
               result = await self._create_activity_use_case.execute(dto, user_id)
               return SuccessResponse(
                   data=result,
                   message="Actividad creada exitosamente"
               )
           except ValidationError as e:
               raise HTTPException(status_code=400, detail=str(e))
           except ForbiddenError as e:
               raise HTTPException(status_code=403, detail=str(e))
           except Exception as e:
               raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def get_activity(self, activity_id: str, current_user: dict):
        """Obtener actividad por ID"""
        try:
            # CORREGIDO: Extraer el ID del usuario del token
            user_id = current_user.get("sub") if isinstance(current_user, dict) else current_user
            result = await self._get_activity_use_case.execute(activity_id, user_id)
            return SuccessResponse(data=result)
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def get_day_activities(self, day_id: str, current_user: dict, include_stats: bool = True):
        """Obtener actividades de un día"""
        try:
            # CORREGIDO: Extraer el ID del usuario del token
            user_id = current_user.get("sub") if isinstance(current_user, dict) else current_user
            result = await self._get_day_activities_use_case.execute(day_id, user_id, include_stats)
            return SuccessResponse(data=result)
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def update_activity(self, activity_id: str, dto: UpdateActivityDTO, current_user: dict):
        """Actualizar actividad"""
        try:
            # CORREGIDO: Extraer el ID del usuario del token
            user_id = current_user.get("sub") if isinstance(current_user, dict) else current_user
            result = await self._update_activity_use_case.execute(activity_id, dto, user_id)
            return SuccessResponse(
                data=result,
                message="Actividad actualizada exitosamente"
            )
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def change_activity_status(self, activity_id: str, dto: ChangeActivityStatusDTO, current_user: dict):
        """Cambiar estado de actividad"""
        try:
            # CORREGIDO: Extraer el ID del usuario del token
            user_id = current_user.get("sub") if isinstance(current_user, dict) else current_user
            result = await self._change_activity_status_use_case.execute(activity_id, dto, user_id)
            return SuccessResponse(
                data=result,
                message="Estado de actividad actualizado exitosamente"
            )
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def reorder_activities(self, day_id: str, dto: ReorderActivitiesDTO, current_user: dict):
        """Reordenar actividades de un día"""
        try:
            # CORREGIDO: Extraer el ID del usuario del token
            user_id = current_user.get("sub") if isinstance(current_user, dict) else current_user
            result = await self._reorder_activities_use_case.execute(day_id, dto, user_id)
            return SuccessResponse(
                data=result,
                message="Actividades reordenadas exitosamente"
            )
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def delete_activity(self, activity_id: str, current_user: dict):
        """Eliminar actividad"""
        try:
            # CORREGIDO: Extraer el ID del usuario del token
            user_id = current_user.get("sub") if isinstance(current_user, dict) else current_user
            await self._delete_activity_use_case.execute(activity_id, user_id)
            return SuccessResponse(
                data=None,
                message="Actividad eliminada exitosamente"
            )
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
        """Eliminar actividad"""
        try:
            await self._delete_activity_use_case.execute(activity_id, current_user)
            return SuccessResponse(
                data=None,
                message="Actividad eliminada exitosamente"
            )
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")