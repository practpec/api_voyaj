from ...domain.interfaces.IPlanRealityDifferenceRepository import IPlanRealityDifferenceRepository
from ...domain.plan_reality_difference_service import PlanRealityDifferenceService
from ..dtos.plan_reality_difference_dto import PlanRealityDifferenceResponseDTO, PlanRealityDifferenceDTOMapper
from shared.errors.custom_errors import NotFoundError, ForbiddenError


class GetPlanRealityDifferenceUseCase:
    """Caso de uso para obtener diferencia por ID"""
    
    def __init__(
        self,
        plan_reality_difference_repository: IPlanRealityDifferenceRepository,
        plan_reality_difference_service: PlanRealityDifferenceService
    ):
        self._repository = plan_reality_difference_repository
        self._service = plan_reality_difference_service

    async def execute(self, difference_id: str, user_id: str) -> PlanRealityDifferenceResponseDTO:
        """Ejecutar obtención de diferencia"""
        # Buscar diferencia
        difference = await self._repository.find_by_id(difference_id)
        if not difference:
            raise NotFoundError("Diferencia no encontrada")

        # Validar acceso al viaje
        has_access = await self._service.validate_trip_access(difference.trip_id, user_id)
        if not has_access:
            raise ForbiddenError("No tienes permisos para acceder a esta diferencia")

        return PlanRealityDifferenceDTOMapper.to_response_dto(difference)