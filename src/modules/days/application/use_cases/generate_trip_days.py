# src/modules/days/application/use_cases/generate_trip_days.py
from typing import List
from datetime import date
from ..dtos.day_dto import GenerateTripDaysDTO, BulkCreateDaysResponseDTO, DayDTOMapper
from ...domain.Day import Day
from ...domain.day_service import DayService
from ...domain.day_events import BulkDaysCreatedEvent
from ...domain.interfaces.day_repository import IDayRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from shared.events.event_bus import EventBus


class GenerateTripDaysUseCase:
    def __init__(
        self,
        day_repository: IDayRepository,
        trip_member_repository: ITripMemberRepository,
        day_service: DayService,
        event_bus: EventBus
    ):
        self._day_repository = day_repository
        self._trip_member_repository = trip_member_repository
        self._day_service = day_service
        self._event_bus = event_bus

    async def execute(self, dto: GenerateTripDaysDTO, user_id: str) -> BulkCreateDaysResponseDTO:
        """Generar automáticamente todos los días de un viaje"""
        try:
            # Generar días usando el service
            created_days = await self._day_service.generate_days_for_trip(dto.trip_id, user_id)
            
            # Convertir a DTOs de respuesta
            day_responses = []
            member = await self._trip_member_repository.find_by_trip_and_user(dto.trip_id, user_id)
            can_edit = member.can_edit_trip() if member else False
            
            for day in created_days:
                day_response = DayDTOMapper.to_day_response(
                    day.to_public_data(),
                    can_edit=can_edit,
                    activity_count=0,
                    photo_count=0
                )
                day_responses.append(day_response)

            # Emitir evento si se crearon días
            if created_days:
                # ✅ Crear evento con argumentos nombrados
                event = BulkDaysCreatedEvent(
                    trip_id=dto.trip_id,
                    day_ids=[day.id for day in created_days],
                    created_by=user_id,
                    total_created=len(created_days)
                )
                await self._event_bus.publish(event)

            return BulkCreateDaysResponseDTO(
                created_days=day_responses,
                total_created=len(created_days),
                skipped_dates=[],  # En este caso no hay fechas saltadas
                message=f"Se generaron {len(created_days)} días exitosamente"
            )

        except Exception as e:
            print(f"[ERROR] Error en GenerateTripDaysUseCase: {str(e)}")
            raise e