from fastapi import HTTPException
from typing import List

from ...application.dtos.plan_reality_difference_dto import (
    CreatePlanRealityDifferenceDTO, 
    PlanRealityDifferenceResponseDTO,
    TripAnalysisResponseDTO
)
from ...application.use_cases.create_plan_reality_difference import CreatePlanRealityDifferenceUseCase
from ...application.use_cases.get_plan_reality_difference import GetPlanRealityDifferenceUseCase
from ...application.use_cases.get_trip_differences import GetTripDifferencesUseCase
from ...application.use_cases.get_trip_analysis import GetTripAnalysisUseCase

from shared.utils.response_utils import SuccessResponse
from shared.errors.custom_errors import NotFoundError, ForbiddenError, ValidationError


class PlanRealityDifferenceController:
    """Controlador para gestión de diferencias plan vs realidad"""
    
    def __init__(
        self,
        create_difference_use_case: CreatePlanRealityDifferenceUseCase,
        get_difference_use_case: GetPlanRealityDifferenceUseCase,
        get_trip_differences_use_case: GetTripDifferencesUseCase,
        get_trip_analysis_use_case: GetTripAnalysisUseCase
    ):
        self._create_difference_use_case = create_difference_use_case
        self._get_difference_use_case = get_difference_use_case
        self._get_trip_differences_use_case = get_trip_differences_use_case
        self._get_trip_analysis_use_case = get_trip_analysis_use_case

    async def create_difference(
        self, 
        dto: CreatePlanRealityDifferenceDTO, 
        current_user: dict
    ) -> SuccessResponse:
        """Crear nueva diferencia plan vs realidad"""
        try:
            result = await self._create_difference_use_case.execute(dto, current_user["id"])
            return SuccessResponse(
                message="Diferencia registrada exitosamente",
                data=result
            )
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def get_difference(
        self, 
        difference_id: str, 
        current_user: dict
    ) -> SuccessResponse:
        """Obtener diferencia por ID"""
        try:
            result = await self._get_difference_use_case.execute(difference_id, current_user["id"])
            return SuccessResponse(
                message="Diferencia obtenida exitosamente",
                data=result
            )
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def get_trip_differences(
        self, 
        trip_id: str, 
        current_user: dict
    ) -> SuccessResponse:
        """Obtener diferencias de un viaje"""
        try:
            result = await self._get_trip_differences_use_case.execute(trip_id, current_user["id"])
            return SuccessResponse(
                message=f"Se obtuvieron {len(result)} diferencias del viaje",
                data=result
            )
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def get_trip_analysis(
        self, 
        trip_id: str, 
        current_user: dict
    ) -> SuccessResponse:
        """Obtener análisis completo del viaje"""
        try:
            result = await self._get_trip_analysis_use_case.execute(trip_id, current_user["id"])
            return SuccessResponse(
                message="Análisis del viaje generado exitosamente",
                data=result
            )
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def health_check(self) -> SuccessResponse:
        """Health check del módulo"""
        return SuccessResponse(
            message="Módulo plan_reality_differences funcionando correctamente",
            data={
                "status": "healthy", 
                "module": "plan_reality_differences",
                "features": [
                    "create_difference", 
                    "get_difference", 
                    "trip_differences",
                    "trip_analysis"
                ]
            }
        )