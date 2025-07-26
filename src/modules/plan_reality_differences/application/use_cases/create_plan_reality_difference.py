from typing import Optional
from ...domain.PlanRealityDifference import PlanRealityDifferenceData
from ...domain.interfaces.IPlanRealityDifferenceRepository import IPlanRealityDifferenceRepository
from ...domain.plan_reality_difference_service import PlanRealityDifferenceService
from ..dtos.plan_reality_difference_dto import CreatePlanRealityDifferenceDTO, PlanRealityDifferenceResponseDTO, PlanRealityDifferenceDTOMapper
from shared.errors.custom_errors import NotFoundError, ForbiddenError, ValidationError


class CreatePlanRealityDifferenceUseCase:
    """Caso de uso para crear diferencia plan vs realidad"""
    
    def __init__(
        self,
        plan_reality_difference_repository: IPlanRealityDifferenceRepository,
        plan_reality_difference_service: PlanRealityDifferenceService
    ):
        self._repository = plan_reality_difference_repository
        self._service = plan_reality_difference_service

    async def execute(self, dto: CreatePlanRealityDifferenceDTO, user_id: str) -> PlanRealityDifferenceResponseDTO:
        """Ejecutar creación de diferencia"""
        # Validar acceso al viaje
        has_access = await self._service.validate_trip_access(dto.trip_id, user_id)
        if not has_access:
            raise ForbiddenError("No tienes permisos para acceder a este viaje")

        # Validar datos
        if not dto.metric or not dto.planned_value or not dto.actual_value:
            raise ValidationError("Métrica, valor planificado y valor real son obligatorios")

        # Crear diferencia
        difference = PlanRealityDifferenceData.create(
            trip_id=dto.trip_id,
            metric=dto.metric,
            planned_value=dto.planned_value,
            actual_value=dto.actual_value,
            notes=dto.notes,
            day_id=dto.day_id,
            activity_id=dto.activity_id
        )

        # Guardar
        saved_difference = await self._repository.save(difference)
        
        return PlanRealityDifferenceDTOMapper.to_response_dto(saved_difference)