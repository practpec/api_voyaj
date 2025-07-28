from ..dtos.trip_member_dto import InviteMemberDTO, TripMemberResponseDTO, TripMemberDTOMapper
from ...domain.trip_member import TripMember
from ...domain.trip_service import TripService
from ...domain.trip_events import MemberInvitedEvent, InvitationSentEvent
from ...domain.interfaces.trip_repository import ITripRepository
from ...domain.interfaces.trip_member_repository import ITripMemberRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from shared.events.event_bus import EventBus
from shared.errors.custom_errors import NotFoundError


class InviteUserToTripUseCase:
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
        dto: InviteMemberDTO, 
        inviter_id: str
    ) -> TripMemberResponseDTO:
        trip = await self._trip_repository.find_by_id(trip_id)
        if not trip or not trip.is_active():
            raise NotFoundError("Viaje no encontrado")

        await self._trip_service.validate_member_invitation(
            trip, 
            inviter_id, 
            dto.user_id, 
            dto.role
        )

        trip_member = TripMember.create_invitation(
            trip_id=trip_id,
            user_id=dto.user_id,
            invited_by=inviter_id,
            role=dto.role,
            notes=dto.notes
        )

        created_member = await self._trip_member_repository.create(trip_member)

        member_invited_event = MemberInvitedEvent(
            trip_id=trip_id,
            invited_user_id=dto.user_id,
            invited_by=inviter_id,
            role=dto.role.value
        )
        await self._event_bus.publish(member_invited_event)

        invitation_sent_event = InvitationSentEvent(
            trip_id=trip_id,
            invited_user_id=dto.user_id,
            invited_by=inviter_id
        )
        await self._event_bus.publish(invitation_sent_event)

        invited_user = await self._user_repository.find_by_id(dto.user_id)
        inviter_user = await self._user_repository.find_by_id(inviter_id)

        return TripMemberDTOMapper.to_member_response(
            created_member.to_public_data(),
            invited_user.to_public_dict() if invited_user else None,
            inviter_user.to_public_dict() if inviter_user else None
        )