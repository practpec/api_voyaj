from ..dtos.activity_dto import ActivityResponseDTO, ActivityDTOMapper
from ...domain.activity_service import ActivityService
from ...domain.interfaces.activity_repository import IActivityRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from modules.days.domain.interfaces.day_repository import IDayRepository
from shared.errors.custom_errors import NotFoundError, ForbiddenError


class GetActivityUseCase:
    def __init__(
        self,
        activity_repository: IActivityRepository,
        day_repository: IDayRepository,
        trip_member_repository: ITripMemberRepository,
        user_repository: IUserRepository,
        activity_service: ActivityService
    ):
        self._activity_repository = activity_repository
        self._day_repository = day_repository
        self._trip_member_repository = trip_member_repository
        self._user_repository = user_repository
        self._activity_service = activity_service

    async def execute(self, activity_id: str, user_id: str) -> ActivityResponseDTO:
        """Obtener actividad específica por ID"""
        activity = await self._activity_repository.find_by_id(activity_id)
        if not activity or not activity.is_active():
            raise NotFoundError("Actividad no encontrada")

        # Verificar acceso del usuario
        can_access = await self._activity_service.can_user_access_activity(activity, user_id)
        if not can_access:
            raise ForbiddenError("No tienes acceso a esta actividad")

        # Obtener información del día para determinar el trip_id
        day = await self._day_repository.find_by_id(activity.day_id)
        if not day:
            raise NotFoundError("Día asociado no encontrado")

        # Determinar permisos del usuario
        member = await self._trip_member_repository.find_by_trip_and_user(day.trip_id, user_id)
        can_edit = member.can_edit_trip() if member else False
        can_change_status = member.is_active() if member else False

        # Obtener información del creador
        creator_user = await self._user_repository.find_by_id(activity.created_by)
        creator_info = creator_user.to_public_data() if creator_user else None

        return ActivityDTOMapper.to_activity_response(
            activity.to_public_data(),
            can_edit=can_edit,
            can_change_status=can_change_status,
            creator_info=creator_info
        )