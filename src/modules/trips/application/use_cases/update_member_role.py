from ..dtos.trip_member_dto import UpdateMemberRoleDTO, TripMemberResponseDTO, TripMemberDTOMapper
from ...domain.trip_service import TripService
from ...domain.trip_events import MemberRoleChangedEvent
from ...domain.interfaces.trip_repository import ITripRepository
from ...domain.interfaces.trip_member_repository import ITripMemberRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from shared.events.event_bus import EventBus
from shared.errors.custom_errors import NotFoundError


class UpdateMemberRoleUseCase:
    def __init__(
        self,
        trip_repository: ITripRepository,
        trip_member_repository: ITripMemberRepository,
        user_repository: IUserRepository,
        trip_service: TripService,
        event_bus: EventBus
    ):
        self._trip_repository = trip_repository
        self._trip_member_repository = trip_member_repository
        self._user_repository = user_repository
        self._trip_service = trip_service
        self._event_bus = event_bus

    async def execute(
        self, 
        trip_id: str, 
        member_id: str, 
        dto: UpdateMemberRoleDTO, 
        admin_user_id: str
    ) -> TripMemberResponseDTO:
        trip = await self._trip_repository.find_by_id(trip_id)
        if not trip or not trip.is_active():
            raise NotFoundError("Viaje no encontrado")

        member = await self._trip_member_repository.find_by_id(member_id)
        if not member or member.trip_id != trip_id:
            raise NotFoundError("Miembro no encontrado")

        await self._trip_service.validate_member_action(trip, admin_user_id, member, "change_role")

        old_role = member.role
        member.change_role(dto.role)

        updated_member = await self._trip_member_repository.update(member)

        event = MemberRoleChangedEvent(
            trip_id=trip_id,
            user_id=member.user_id,
            old_role=old_role,
            new_role=dto.role.value,
            changed_by=admin_user_id
        )
        await self._event_bus.publish(event)

        user_info = await self._user_repository.find_by_id(member.user_id)
        admin_info = await self._user_repository.find_by_id(admin_user_id)

        return TripMemberDTOMapper.to_member_response(
            updated_member.to_public_data(),
            user_info.to_public_data() if user_info else None,
            admin_info.to_public_data() if admin_info else None
        )