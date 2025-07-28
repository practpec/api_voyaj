from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import Annotated, Optional
from datetime import date

from ...application.dtos.day_dto import (
    CreateDayDTO, UpdateDayDTO, GenerateTripDaysDTO,
    DayResponseDTO, TripTimelineResponseDTO, BulkCreateDaysResponseDTO
)
from ...application.use_cases.create_day import CreateDayUseCase
from ...application.use_cases.get_day import GetDayUseCase
from ...application.use_cases.get_trip_days import GetTripDaysUseCase
from ...application.use_cases.update_day import UpdateDayUseCase
from ...application.use_cases.delete_day import DeleteDayUseCase
from ...application.use_cases.generate_trip_days import GenerateTripDaysUseCase

from shared.middleware.AuthMiddleware import get_current_user
from shared.utils.response_utils import SuccessResponse
from shared.utils.validation_utils import ValidationUtils


class DayController:
    def __init__(
        self,
        create_day_use_case: CreateDayUseCase,
        get_day_use_case: GetDayUseCase,
        get_trip_days_use_case: GetTripDaysUseCase,
        update_day_use_case: UpdateDayUseCase,
        delete_day_use_case: DeleteDayUseCase,
        generate_trip_days_use_case: GenerateTripDaysUseCase
    ):
        self.router = APIRouter(prefix="/api/days", tags=["days"])
        self._create_day_use_case = create_day_use_case
        self._get_day_use_case = get_day_use_case
        self._get_trip_days_use_case = get_trip_days_use_case
        self._update_day_use_case = update_day_use_case
        self._delete_day_use_case = delete_day_use_case
        self._generate_trip_days_use_case = generate_trip_days_use_case
        
        self._setup_routes()

    def _setup_routes(self):
        self.router.add_api_route(
            "/",
            self.create_day,
            methods=["POST"],
            response_model=SuccessResponse[DayResponseDTO]
        )
        self.router.add_api_route(
            "/{day_id}",
            self.get_day,
            methods=["GET"],
            response_model=SuccessResponse[DayResponseDTO]
        )
        self.router.add_api_route(
            "/{day_id}",
            self.update_day,
            methods=["PUT"],
            response_model=SuccessResponse[DayResponseDTO]
        )
        self.router.add_api_route(
            "/{day_id}",
            self.delete_day,
            methods=["DELETE"],
            response_model=SuccessResponse[bool]
        )
        self.router.add_api_route(
            "/trip/{trip_id}/timeline",
            self.get_trip_timeline,
            methods=["GET"],
            response_model=SuccessResponse[TripTimelineResponseDTO]
        )
        self.router.add_api_route(
            "/trip/{trip_id}/generate",
            self.generate_trip_days,
            methods=["POST"],
            response_model=SuccessResponse[BulkCreateDaysResponseDTO]
        )

    async def create_day(
        self,
        dto: CreateDayDTO,
        current_user: Annotated[dict, Depends(get_current_user)]
    ) -> SuccessResponse[DayResponseDTO]:
        """Crear nuevo día en un viaje"""
        try:
            print(f"[DEBUG] Creando día: {dto.trip_id}, {dto.date}")
            
            validation_result = ValidationUtils.validate_uuid(dto.trip_id)
            if not validation_result.is_valid:
                raise HTTPException(status_code=400, detail="ID de viaje inválido")

            result = await self._create_day_use_case.execute(dto, current_user["sub"])
            
            return SuccessResponse(
                data=result,
                message="Día creado exitosamente"
            )
            
        except ValueError as e:
            print(f"[ERROR] ValueError en create_day: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            print(f"[ERROR] Exception en create_day: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def get_day(
        self,
        day_id: Annotated[str, Path()],
        current_user: Annotated[dict, Depends(get_current_user)]
    ) -> SuccessResponse[DayResponseDTO]:
        """Obtener día específico"""
        try:
            print(f"[DEBUG] Obteniendo día: {day_id}")
            
            validation_result = ValidationUtils.validate_uuid(day_id)
            if not validation_result.is_valid:
                raise HTTPException(status_code=400, detail="ID de día inválido")

            result = await self._get_day_use_case.execute(day_id, current_user["sub"])
            
            return SuccessResponse(
                data=result,
                message="Día obtenido exitosamente"
            )
            
        except ValueError as e:
            print(f"[ERROR] ValueError en get_day: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            print(f"[ERROR] Exception en get_day: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def update_day(
        self,
        day_id: Annotated[str, Path()],
        dto: UpdateDayDTO,
        current_user: Annotated[dict, Depends(get_current_user)]
    ) -> SuccessResponse[DayResponseDTO]:
        """Actualizar día existente"""
        try:
            print(f"[DEBUG] Actualizando día: {day_id}")
            
            validation_result = ValidationUtils.validate_uuid(day_id)
            if not validation_result.is_valid:
                raise HTTPException(status_code=400, detail="ID de día inválido")

            result = await self._update_day_use_case.execute(
                day_id, dto, current_user["sub"]
            )
            
            return SuccessResponse(
                data=result,
                message="Día actualizado exitosamente"
            )
            
        except ValueError as e:
            print(f"[ERROR] ValueError en update_day: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            print(f"[ERROR] Exception en update_day: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def delete_day(
        self,
        day_id: Annotated[str, Path()],
        current_user: Annotated[dict, Depends(get_current_user)]
    ) -> SuccessResponse[bool]:
        """Eliminar día"""
        try:
            print(f"[DEBUG] Eliminando día: {day_id}")
            
            validation_result = ValidationUtils.validate_uuid(day_id)
            if not validation_result.is_valid:
                raise HTTPException(status_code=400, detail="ID de día inválido")

            result = await self._delete_day_use_case.execute(day_id, current_user["sub"])
            
            return SuccessResponse(
                data=result,
                message="Día eliminado exitosamente"
            )
            
        except ValueError as e:
            print(f"[ERROR] ValueError en delete_day: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            print(f"[ERROR] Exception en delete_day: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def get_trip_timeline(
        self,
        trip_id: Annotated[str, Path()],
        current_user: Annotated[dict, Depends(get_current_user)]
    ) -> SuccessResponse[TripTimelineResponseDTO]:
        """Obtener timeline de días del viaje"""
        try:
            print(f"[DEBUG] Obteniendo timeline: {trip_id}")
            
            validation_result = ValidationUtils.validate_uuid(trip_id)
            if not validation_result.is_valid:
                raise HTTPException(status_code=400, detail="ID de viaje inválido")

            result = await self._get_trip_days_use_case.execute(trip_id, current_user["sub"])
            
            return SuccessResponse(
                data=result,
                message="Timeline obtenido exitosamente"
            )
            
        except ValueError as e:
            print(f"[ERROR] ValueError en get_trip_timeline: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            print(f"[ERROR] Exception en get_trip_timeline: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def generate_trip_days(
        self,
        trip_id: Annotated[str, Path()],
        current_user: Annotated[dict, Depends(get_current_user)]
    ) -> SuccessResponse[BulkCreateDaysResponseDTO]:
        """Generar automáticamente todos los días del viaje"""
        try:
            print(f"[DEBUG] Generando días: {trip_id}")
            
            validation_result = ValidationUtils.validate_uuid(trip_id)
            if not validation_result.is_valid:
                raise HTTPException(status_code=400, detail="ID de viaje inválido")

            dto = GenerateTripDaysDTO(trip_id=trip_id)
            result = await self._generate_trip_days_use_case.execute(dto, current_user["sub"])
            
            return SuccessResponse(
                data=result,
                message=f"Se generaron {result.total_created} días exitosamente"
            )
            
        except ValueError as e:
            print(f"[ERROR] ValueError en generate_trip_days: {str(e)}")  
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            print(f"[ERROR] Exception en generate_trip_days: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")