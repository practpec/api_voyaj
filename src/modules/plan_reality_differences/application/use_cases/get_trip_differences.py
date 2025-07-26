from typing import List
from ...domain.interfaces.IPlanRealityDifferenceRepository import IPlanRealityDifferenceRepository
from ...domain.plan_reality_difference_service import PlanRealityDifferenceService
from ..dtos.plan_reality_difference_dto import PlanRealityDifferenceResponseDTO, PlanRealityDifferenceDTOMapper
from shared.errors.custom_errors import ForbiddenError


class GetTripDifferencesUseCase:
    """Caso de uso para obtener diferencias de un viaje"""
    
    def __init__(
        self,
        plan_reality_difference_repository: IPlanRealityDifferenceRepository,
        plan_reality_difference_service: PlanRealityDifferenceService
    ):
        self._repository = plan_reality_difference_repository
        self._service = plan_reality_difference_service

    async def execute(self, trip_id: str, user_id: str) -> List[PlanRealityDifferenceResponseDTO]:
        """Ejecutar obtención de diferencias del viaje"""
        # Validar acceso al viaje
        has_access = await self._service.validate_trip_access(trip_id, user_id)
        if not has_access:
            raise ForbiddenError("No tienes permisos para acceder a este viaje")

        # Obtener diferencias
        differences = await self._repository.find_by_trip_id(trip_id)
        
        return [
            PlanRealityDifferenceDTOMapper.to_response_dto(diff)
            for diff in differences
        ]