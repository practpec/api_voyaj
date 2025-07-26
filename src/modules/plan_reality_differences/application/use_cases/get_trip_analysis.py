from ...domain.plan_reality_difference_service import PlanRealityDifferenceService
from ..dtos.plan_reality_difference_dto import TripAnalysisResponseDTO, PlanRealityDifferenceDTOMapper
from shared.errors.custom_errors import ForbiddenError


class GetTripAnalysisUseCase:
    """Caso de uso para obtener análisis del viaje"""
    
    def __init__(
        self,
        plan_reality_difference_service: PlanRealityDifferenceService
    ):
        self._service = plan_reality_difference_service

    async def execute(self, trip_id: str, user_id: str) -> TripAnalysisResponseDTO:
        """Ejecutar análisis del viaje"""
        # Validar acceso al viaje
        has_access = await self._service.validate_trip_access(trip_id, user_id)
        if not has_access:
            raise ForbiddenError("No tienes permisos para acceder a este viaje")

        # Obtener análisis
        analysis = await self._service.get_trip_analysis(trip_id)
        
        # Mapear diferencias importantes
        major_variances = [
            PlanRealityDifferenceDTOMapper.to_response_dto(diff)
            for diff in analysis["major_variances"]
        ]
        
        return TripAnalysisResponseDTO(
            trip_id=trip_id,
            trip_title="",  # Se completará con información del trip
            total_differences=analysis["total_differences"],
            differences_by_metric=analysis["differences_by_metric"],
            major_variances=major_variances,
            budget_variance=analysis["budget_variance"],
            time_variance=analysis["time_variance"],
            overall_satisfaction=analysis["overall_satisfaction"],
            recommendations=analysis["recommendations"]
        )