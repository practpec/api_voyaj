from typing import List
from fastapi import HTTPException
from ...application.dtos.diary_entry_dto import (
    CreateDiaryEntryDTO, 
    UpdateDiaryEntryDTO, 
    AddEmotionDTO,
    DiaryEntryResponseDTO,
    DiaryEntryStatsDTO
)
from ...application.use_cases.create_diary_entry import CreateDiaryEntryUseCase
from ...application.use_cases.get_diary_entry import GetDiaryEntryUseCase
from ...application.use_cases.get_day_diary_entries import GetDayDiaryEntriesUseCase
from ...application.use_cases.update_diary_entry import UpdateDiaryEntryUseCase
from ...application.use_cases.delete_diary_entry import DeleteDiaryEntryUseCase
from ...application.use_cases.add_emotion import AddEmotionUseCase
from ...application.use_cases.get_trip_diary_stats import GetTripDiaryStatsUseCase
from shared.errors.custom_errors import NotFoundError, ValidationError, ForbiddenError


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
        self._create_diary_entry_use_case = create_diary_entry_use_case
        self._get_diary_entry_use_case = get_diary_entry_use_case
        self._get_day_diary_entries_use_case = get_day_diary_entries_use_case
        self._update_diary_entry_use_case = update_diary_entry_use_case
        self._delete_diary_entry_use_case = delete_diary_entry_use_case
        self._add_emotion_use_case = add_emotion_use_case
        self._get_trip_diary_stats_use_case = get_trip_diary_stats_use_case

    async def create_diary_entry(self, dto: CreateDiaryEntryDTO, current_user: dict) -> DiaryEntryResponseDTO:
        try:
            user_id = current_user.get("sub")
            return await self._create_diary_entry_use_case.execute(dto, user_id)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    async def get_diary_entry(self, entry_id: str, current_user: dict) -> DiaryEntryResponseDTO:
        try:
            user_id = current_user.get("sub")
            return await self._get_diary_entry_use_case.execute(entry_id, user_id)
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    async def get_day_diary_entries(self, day_id: str, current_user: dict) -> List[DiaryEntryResponseDTO]:
        try:
            user_id = current_user.get("sub")
            return await self._get_day_diary_entries_use_case.execute(day_id, user_id)
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    async def update_diary_entry(
        self, 
        entry_id: str, 
        dto: UpdateDiaryEntryDTO, 
        current_user: dict
    ) -> DiaryEntryResponseDTO:
        try:
            user_id = current_user.get("sub")
            return await self._update_diary_entry_use_case.execute(entry_id, dto, user_id)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    async def delete_diary_entry(self, entry_id: str, current_user: dict) -> dict:
        try:
            user_id = current_user.get("sub")
            success = await self._delete_diary_entry_use_case.execute(entry_id, user_id)
            if success:
                return {"message": "Entrada eliminada exitosamente"}
            else:
                raise HTTPException(status_code=500, detail="No se pudo eliminar la entrada")
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    async def add_emotion(
        self, 
        entry_id: str, 
        dto: AddEmotionDTO, 
        current_user: dict
    ) -> DiaryEntryResponseDTO:
        try:
            user_id = current_user.get("sub")
            return await self._add_emotion_use_case.execute(entry_id, dto, user_id)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    async def get_trip_diary_stats(self, trip_id: str, current_user: dict) -> DiaryEntryStatsDTO:
        try:
            user_id = current_user.get("sub")
            return await self._get_trip_diary_stats_use_case.execute(trip_id, user_id)
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error interno del servidor")