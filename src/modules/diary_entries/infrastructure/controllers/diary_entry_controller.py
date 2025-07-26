from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import Annotated, Optional

from ...application.dtos.diary_entry_dto import (
    CreateDiaryEntryDTO, UpdateDiaryEntryDTO, AddEmotionDTO,
    DiaryEntryResponseDTO, DayDiaryEntriesResponseDTO, TripDiaryStatsDTO
)
from ...application.use_cases.create_diary_entry import CreateDiaryEntryUseCase
from ...application.use_cases.get_diary_entry import GetDiaryEntryUseCase
from ...application.use_cases.get_day_diary_entries import GetDayDiaryEntriesUseCase
from ...application.use_cases.update_diary_entry import UpdateDiaryEntryUseCase
from ...application.use_cases.delete_diary_entry import DeleteDiaryEntryUseCase
from ...application.use_cases.add_emotion import AddEmotionUseCase
from ...application.use_cases.get_trip_diary_stats import GetTripDiaryStatsUseCase

from shared.middleware.AuthMiddleware import get_current_user
from shared.utils.response_utils import SuccessResponse
from shared.utils.validation_utils import ValidationUtils


class DiaryEntryController:
    def __init__(
        self,
        create_diary_entry_use_case: CreateDiaryEntryUseCase,
        get_diary_entry_use_case: GetDiaryEntryUseCase,
        get_day_diary_entries_use_case: GetDayDiaryEntriesUseCase,
        update_diary_entry_use_case: UpdateDiaryEntryUseCase,
        delete_diary_entry_use_case: DeleteDiaryEntryUseCase,
        add_emotion_use_case: AddEmotionUseCase,
        get_trip_diary_stats_use_case: GetTripDiaryStatsUseCase
    ):
        self.router = APIRouter(prefix="/api/diary", tags=["diary-entries"])
        self._create_diary_entry_use_case = create_diary_entry_use_case
        self._get_diary_entry_use_case = get_diary_entry_use_case
        self._get_day_diary_entries_use_case = get_day_diary_entries_use_case
        self._update_diary_entry_use_case = update_diary_entry_use_case
        self._delete_diary_entry_use_case = delete_diary_entry_use_case
        self._add_emotion_use_case = add_emotion_use_case
        self._get_trip_diary_stats_use_case = get_trip_diary_stats_use_case
        
        self._setup_routes()

    def _setup_routes(self):
        """Configurar todas las rutas del controlador"""
        self.router.add_api_route(
            "/",
            self.create_diary_entry,
            methods=["POST"],
            response_model=SuccessResponse[DiaryEntryResponseDTO]
        )
        self.router.add_api_route(
            "/{entry_id}",
            self.get_diary_entry,
            methods=["GET"],
            response_model=SuccessResponse[DiaryEntryResponseDTO]
        )
        self.router.add_api_route(
            "/{entry_id}",
            self.update_diary_entry,
            methods=["PUT"],
            response_model=SuccessResponse[DiaryEntryResponseDTO]
        )
        self.router.add_api_route(
            "/{entry_id}",
            self.delete_diary_entry,
            methods=["DELETE"],
            response_model=SuccessResponse[bool]
        )
        self.router.add_api_route(
            "/{entry_id}/emotions",
            self.add_emotion,
            methods=["POST"],
            response_model=SuccessResponse[DiaryEntryResponseDTO]
        )
        self.router.add_api_route(
            "/day/{day_id}",
            self.get_day_diary_entries,
            methods=["GET"],
            response_model=SuccessResponse[DayDiaryEntriesResponseDTO]
        )
        self.router.add_api_route(
            "/trip/{trip_id}/stats",
            self.get_trip_diary_stats,
            methods=["GET"],
            response_model=SuccessResponse[TripDiaryStatsDTO]
        )

    async def create_diary_entry(
        self,
        dto: CreateDiaryEntryDTO,
        current_user: Annotated[dict, Depends(get_current_user)]
    ) -> SuccessResponse[DiaryEntryResponseDTO]:
        """Crear nueva entrada de diario"""
        try:
            validation_result = ValidationUtils.validate_uuid(dto.day_id)
            if not validation_result.is_valid:
                raise HTTPException(status_code=400, detail="ID de día inválido")

            result = await self._create_diary_entry_use_case.execute(dto, current_user["sub"])
            
            return SuccessResponse(
                data=result,
                message="Entrada de diario creada exitosamente"
            )
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_diary_entry(
        self,
        entry_id: Annotated[str, Path()],
        current_user: Annotated[dict, Depends(get_current_user)]
    ) -> SuccessResponse[DiaryEntryResponseDTO]:
        """Obtener detalles de una entrada de diario"""
        try:
            validation_result = ValidationUtils.validate_uuid(entry_id)
            if not validation_result.is_valid:
                raise HTTPException(status_code=400, detail="ID de entrada inválido")

            result = await self._get_diary_entry_use_case.execute(entry_id, current_user["sub"])
            
            return SuccessResponse(
                data=result,
                message="Entrada de diario obtenida exitosamente"
            )
            
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))

    async def update_diary_entry(
        self,
        entry_id: Annotated[str, Path()],
        dto: UpdateDiaryEntryDTO,
        current_user: Annotated[dict, Depends(get_current_user)]
    ) -> SuccessResponse[DiaryEntryResponseDTO]:
        """Actualizar entrada de diario existente"""
        try:
            validation_result = ValidationUtils.validate_uuid(entry_id)
            if not validation_result.is_valid:
                raise HTTPException(status_code=400, detail="ID de entrada inválido")

            result = await self._update_diary_entry_use_case.execute(
                entry_id, 
                dto, 
                current_user["sub"]
            )
            
            return SuccessResponse(
                data=result,
                message="Entrada de diario actualizada exitosamente"
            )
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def delete_diary_entry(
        self,
        entry_id: Annotated[str, Path()],
        current_user: Annotated[dict, Depends(get_current_user)]
    ) -> SuccessResponse[bool]:
        """Eliminar entrada de diario"""
        try:
            validation_result = ValidationUtils.validate_uuid(entry_id)
            if not validation_result.is_valid:
                raise HTTPException(status_code=400, detail="ID de entrada inválido")

            result = await self._delete_diary_entry_use_case.execute(
                entry_id, 
                current_user["sub"]
            )
            
            return SuccessResponse(
                data=result,
                message="Entrada de diario eliminada exitosamente"
            )
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def add_emotion(
        self,
        entry_id: Annotated[str, Path()],
        dto: AddEmotionDTO,
        current_user: Annotated[dict, Depends(get_current_user)]
    ) -> SuccessResponse[DiaryEntryResponseDTO]:
        """Agregar emoción a una entrada de diario"""
        try:
            validation_result = ValidationUtils.validate_uuid(entry_id)
            if not validation_result.is_valid:
                raise HTTPException(status_code=400, detail="ID de entrada inválido")

            result = await self._add_emotion_use_case.execute(
                entry_id,
                dto,
                current_user["sub"]
            )
            
            return SuccessResponse(
                data=result,
                message="Emoción agregada exitosamente"
            )
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_day_diary_entries(
        self,
        day_id: Annotated[str, Path()],
        current_user: Annotated[dict, Depends(get_current_user)],
        include_stats: Annotated[bool, Query()] = True
    ) -> SuccessResponse[DayDiaryEntriesResponseDTO]:
        """Obtener entradas de diario de un día"""
        try:
            validation_result = ValidationUtils.validate_uuid(day_id)
            if not validation_result.is_valid:
                raise HTTPException(status_code=400, detail="ID de día inválido")

            result = await self._get_day_diary_entries_use_case.execute(
                day_id, 
                current_user["sub"],
                include_stats
            )
            
            return SuccessResponse(
                data=result,
                message="Entradas de diario del día obtenidas exitosamente"
            )
            
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))

    async def get_trip_diary_stats(
        self,
        trip_id: Annotated[str, Path()],
        current_user: Annotated[dict, Depends(get_current_user)]
    ) -> SuccessResponse[TripDiaryStatsDTO]:
        """Obtener estadísticas del diario del viaje"""
        try:
            validation_result = ValidationUtils.validate_uuid(trip_id)
            if not validation_result.is_valid:
                raise HTTPException(status_code=400, detail="ID de viaje inválido")

            result = await self._get_trip_diary_stats_use_case.execute(
                trip_id,
                current_user["sub"]
            )
            
            return SuccessResponse(
                data=result,
                message="Estadísticas del diario obtenidas exitosamente"
            )
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))