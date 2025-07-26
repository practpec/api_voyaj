from typing import List, Optional
from datetime import datetime
from .trip import Trip, TripStatus
from .trip_member import TripMember, TripMemberRole, TripMemberStatus
from .interfaces.trip_repository import ITripRepository
from .interfaces.trip_member_repository import ITripMemberRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from shared.errors.custom_errors import NotFoundError, ValidationError, ForbiddenError


class TripService:
    def __init__(
        self,
        trip_repository: ITripRepository,
        trip_member_repository: ITripMemberRepository,
        user_repository: IUserRepository
    ):
        self._trip_repository = trip_repository
        self._trip_member_repository = trip_member_repository
        self._user_repository = user_repository

    async def validate_trip_creation(
        self,
        title: str,
        start_date: datetime,
        end_date: datetime,
        owner_id: str
    ):
        if not title or len(title.strip()) < 3:
            raise ValidationError("El título debe tener al menos 3 caracteres")
        
        if start_date >= end_date:
            raise ValidationError("La fecha de inicio debe ser anterior a la fecha de fin")
        
        if start_date < datetime.utcnow():
            raise ValidationError("La fecha de inicio no puede ser en el pasado")
        
        user = await self._user_repository.find_by_id(owner_id)
        if not user:
            raise NotFoundError("Usuario no encontrado")

    async def validate_trip_update(self, trip: Trip, user_id: str, **updates):
        if not trip.is_active():
            raise ValidationError("No se puede actualizar un viaje eliminado")
        
        member = await self._trip_member_repository.find_by_trip_and_user(trip.id, user_id)
        if not member or not member.can_edit_trip():
            raise ForbiddenError("No tienes permisos para editar este viaje")
        
        if 'start_date' in updates and 'end_date' in updates:
            if updates['start_date'] >= updates['end_date']:
                raise ValidationError("La fecha de inicio debe ser anterior a la fecha de fin")

    async def validate_member_invitation(
        self,
        trip: Trip,
        inviter_id: str,
        invited_user_id: str,
        role: TripMemberRole = TripMemberRole.MEMBER
    ):
        if not trip.is_active():
            raise ValidationError("No se pueden enviar invitaciones a viajes eliminados")
        
        if trip.status == TripStatus.COMPLETED.value:
            raise ValidationError("No se pueden enviar invitaciones a viajes completados")
        
        inviter_member = await self._trip_member_repository.find_by_trip_and_user(trip.id, inviter_id)
        if not inviter_member or not inviter_member.can_invite_members():
            raise ForbiddenError("No tienes permisos para invitar miembros")
        
        invited_user = await self._user_repository.find_by_id(invited_user_id)
        if not invited_user:
            raise NotFoundError("Usuario invitado no encontrado")
        
        if inviter_id == invited_user_id:
            raise ValidationError("No puedes invitarte a ti mismo")
        
        existing_member = await self._trip_member_repository.find_by_trip_and_user(trip.id, invited_user_id)
        if existing_member:
            if existing_member.status == TripMemberStatus.PENDING.value:
                raise ValidationError("El usuario ya tiene una invitación pendiente")
            elif existing_member.status == TripMemberStatus.ACCEPTED.value:
                raise ValidationError("El usuario ya es miembro del viaje")
            elif existing_member.status in [TripMemberStatus.REJECTED.value, TripMemberStatus.LEFT.value]:
                pass
        
        if role == TripMemberRole.OWNER:
            raise ValidationError("No se puede invitar a alguien como propietario")

    async def validate_member_action(
        self,
        trip: Trip,
        actor_id: str,
        target_member: TripMember,
        action: str
    ):
        if not trip.is_active():
            raise ValidationError("No se pueden realizar acciones en viajes eliminados")
        
        actor_member = await self._trip_member_repository.find_by_trip_and_user(trip.id, actor_id)
        if not actor_member:
            raise ForbiddenError("No eres miembro de este viaje")
        
        if action == "accept_invitation":
            if target_member.user_id != actor_id:
                raise ForbiddenError("Solo puedes aceptar tus propias invitaciones")
            if target_member.status != TripMemberStatus.PENDING.value:
                raise ValidationError("Solo se pueden aceptar invitaciones pendientes")
        
        elif action == "reject_invitation":
            if target_member.user_id != actor_id:
                raise ForbiddenError("Solo puedes rechazar tus propias invitaciones")
            if target_member.status != TripMemberStatus.PENDING.value:
                raise ValidationError("Solo se pueden rechazar invitaciones pendientes")
        
        elif action == "remove_member":
            if not actor_member.can_edit_trip():
                raise ForbiddenError("No tienes permisos para remover miembros")
            if target_member.is_owner():
                raise ValidationError("No se puede remover al propietario del viaje")
        
        elif action == "change_role":
            if not actor_member.can_edit_trip():
                raise ForbiddenError("No tienes permisos para cambiar roles")
            if target_member.is_owner():
                raise ValidationError("No se puede cambiar el rol del propietario")
        
        elif action == "leave_trip":
            if target_member.user_id != actor_id:
                raise ForbiddenError("Solo puedes abandonar el viaje por ti mismo")
            if target_member.is_owner():
                raise ValidationError("El propietario no puede abandonar el viaje")

    async def validate_trip_deletion(self, trip: Trip, user_id: str):
        if not trip.is_owner(user_id):
            raise ForbiddenError("Solo el propietario puede eliminar el viaje")
        
        if not trip.is_active():
            raise ValidationError("El viaje ya está eliminado")

    async def calculate_trip_stats(self, trip_id: str) -> dict:
        members = await self._trip_member_repository.find_active_members_by_trip_id(trip_id)
        pending_invitations = await self._trip_member_repository.find_pending_members_by_trip_id(trip_id)
        
        return {
            "total_members": len(members),
            "pending_invitations": len(pending_invitations),
            "admins_count": len([m for m in members if m.role in [TripMemberRole.OWNER.value, TripMemberRole.ADMIN.value]]),
            "regular_members_count": len([m for m in members if m.role == TripMemberRole.MEMBER.value])
        }

    async def can_user_access_trip(self, trip: Trip, user_id: str) -> bool:
        if trip.is_public:
            return True
        
        if trip.is_owner(user_id):
            return True
        
        return await self._trip_member_repository.can_user_access_trip(trip.id, user_id)

    async def get_user_role_in_trip(self, trip_id: str, user_id: str) -> Optional[str]:
        member = await self._trip_member_repository.find_by_trip_and_user(trip_id, user_id)
        return member.role if member and member.is_active() else None

    async def suggest_similar_destinations(self, destination: str, user_id: str, limit: int = 5) -> List[str]:
        user_trips = await self._trip_repository.find_active_by_owner_id(user_id)
        destinations = [trip.destination for trip in user_trips if trip.destination != destination]
        
        return list(set(destinations))[:limit]