from typing import List
from ..dtos.day_dto import TripTimelineResponseDTO, DayListResponseDTO, DayDTOMapper
from ...domain.day_service import DayService
from ...domain.interfaces.day_repository import IDayRepository


class GetTripDaysUseCase:
    def __init__(
        self,
        day_repository: IDayRepository,
        day_service: DayService
    ):
        self._day_repository = day_repository
        self._day_service = day_service

    async def execute(self, trip_id: str, user_id: str) -> TripTimelineResponseDTO:
        """Obtener todos los días de un viaje como timeline"""
        days = await self._day_service.get_trip_timeline(trip_id, user_id)
        
        day_list_responses: List[DayListResponseDTO] = []
        
        for day in days:
            # TODO: Implementar conteo de actividades y fotos cuando estén disponibles
            activity_count = 0
            photo_count = 0
            
            day_response = DayDTOMapper.to_day_list_response(
                day.to_public_data(),
                activity_count=activity_count,
                photo_count=photo_count
            )
            day_list_responses.append(day_response)

        stats = await self._day_service.get_day_statistics(trip_id)
        days_with_content = len([d for d in day_list_responses if d.has_content])
        
        stats_with_content = {
            **stats,
            "days_with_content": days_with_content
        }

        return DayDTOMapper.to_timeline_response(
            trip_id,
            day_list_responses,
            stats_with_content
        )