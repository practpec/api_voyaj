# src/modules/trips/application/use_cases/handle_trip_invitation.py
from ..dtos.trip_member_dto import HandleInvitationDTO, TripMemberResponseDTO, TripMemberDTOMapper
from ...domain.trip_service import TripService
from ...domain.trip_events import InvitationAcceptedEvent, InvitationRejectedEvent, MemberJoinedEvent
from ...domain.interfaces.trip_repository import ITripRepository
from ...domain.interfaces.trip_member_repository import ITripMemberRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from shared.events.event_bus import EventBus
from shared.errors.custom_errors import NotFoundError, ValidationError


class HandleTripInvitationUseCase:
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
        dto: HandleInvitationDTO, 
        user_id: str
    ) -> TripMemberResponseDTO:
        """Manejar aceptación o rechazo de invitación"""
        
        # Validar acción
        if dto.action not in ["accept", "reject"]:
            raise ValidationError("Acción debe ser 'accept' o 'reject'")
        
        # Obtener viaje
        trip = await self._trip_repository.find_by_id(trip_id)
        if not trip or not trip.is_active():
            raise NotFoundError("Viaje no encontrado")

        # Buscar invitación del usuario actual (no usar member_id del parámetro)
        member = await self._trip_member_repository.find_by_trip_and_user(trip_id, user_id)
        if not member:
            raise NotFoundError("No tienes una invitación para este viaje")

        # Validar que la invitación esté pendiente - USANDO PROPIEDAD
        if member.status != "pending":
            raise ValidationError("Solo se pueden procesar invitaciones pendientes")

        # Validar acción específica
        await self._trip_service.validate_member_action(
            trip, user_id, member, f"{dto.action}_invitation"
        )

        # Procesar según la acción
        if dto.action == "accept":
            member.accept_invitation()
            
            # Publicar eventos - USANDO PROPIEDADES
            accepted_event = InvitationAcceptedEvent(
                trip_id=trip_id,
                user_id=user_id,
                invitation_id=member.id
            )
            await self._event_bus.publish(accepted_event)

            joined_event = MemberJoinedEvent(
                trip_id=trip_id,
                user_id=user_id,
                role=member.role
            )
            await self._event_bus.publish(joined_event)

        elif dto.action == "reject":
            member.reject_invitation()
            
            # Publicar evento - USANDO PROPIEDADES
            rejected_event = InvitationRejectedEvent(
                trip_id=trip_id,
                user_id=user_id,
                invitation_id=member.id
            )
            await self._event_bus.publish(rejected_event)

        # Actualizar en base de datos
        updated_member = await self._trip_member_repository.update(member)

        # Obtener información de usuarios para respuesta - USANDO PROPIEDADES
        user_info = await self._user_repository.find_by_id(member.user_id)
        inviter_info = None
        if member.invited_by:  # Ahora funciona porque invited_by es una propiedad
            inviter_info = await self._user_repository.find_by_id(member.invited_by)

        # Retornar respuesta
        return TripMemberDTOMapper.to_member_response(
            updated_member.to_public_data(),
            user_info.to_public_dict() if user_info else None,
            inviter_info.to_public_dict() if inviter_info else None
        )