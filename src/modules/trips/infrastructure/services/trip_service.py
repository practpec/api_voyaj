# src/modules/trips/domain/trip_service.py
from typing import List, Optional
from datetime import datetime
from ...domain.trip import Trip, TripStatus
from ...domain.trip_member import TripMember, TripMemberRole, TripMemberStatus
from ...domain.interfaces.trip_repository import ITripRepository
from ...domain.interfaces.trip_member_repository import ITripMemberRepository
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
        """Validar datos para creación de viaje"""
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
        """Validar actualización de viaje"""
        if not trip.is_active():
            raise ValidationError("No se puede actualizar un viaje eliminado")
        
        member = await self._trip_member_repository.find_by_trip_and_user(trip.id, user_id)
        if not member or not member.can_edit_trip():
            raise ForbiddenError("No tienes permisos para editar este viaje")
        
        # Validar fechas si se están actualizando
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
        """Validar invitación de miembro"""
        if not trip.is_active():
            raise ValidationError("No se pueden enviar invitaciones a viajes eliminados")
        
        if trip.status == TripStatus.COMPLETED.value:
            raise ValidationError("No se pueden enviar invitaciones a viajes completados")
        
        # Verificar permisos del que invita
        inviter_member = await self._trip_member_repository.find_by_trip_and_user(trip.id, inviter_id)
        if not inviter_member or not inviter_member.can_invite_members():
            raise ForbiddenError("No tienes permisos para invitar miembros")
        
        # Verificar que el usuario invitado existe
        invited_user = await self._user_repository.find_by_id(invited_user_id)
        if not invited_user:
            raise NotFoundError("Usuario invitado no encontrado")
        
        # No se puede invitar a sí mismo
        if inviter_id == invited_user_id:
            raise ValidationError("No puedes invitarte a ti mismo")
        
        # Verificar estado actual del usuario en el viaje
        existing_member = await self._trip_member_repository.find_by_trip_and_user(trip.id, invited_user_id)
        if existing_member:
            if existing_member.status == TripMemberStatus.PENDING.value:
                raise ValidationError("El usuario ya tiene una invitación pendiente")
            elif existing_member.status == TripMemberStatus.ACCEPTED.value:
                raise ValidationError("El usuario ya es miembro del viaje")
            elif existing_member.status in [TripMemberStatus.REJECTED.value, TripMemberStatus.LEFT.value]:
                # Permitir re-invitar usuarios que rechazaron o abandonaron
                pass
        
        # No se puede invitar como propietario
        if role == TripMemberRole.OWNER:
            raise ValidationError("No se puede invitar a alguien como propietario")

    async def validate_member_action(
        self,
        trip: Trip,
        actor_id: str,
        target_member: TripMember,
        action: str
    ):
        """Validar acciones sobre miembros del viaje"""
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
                await self._validate_owner_leaving(trip, target_member)

    async def _validate_owner_leaving(self, trip: Trip, owner_member: TripMember):
        """Validar que el propietario pueda abandonar el viaje"""
        # Verificar si hay otros admins que puedan tomar control
        admin_members = await self._trip_member_repository.find_admins_by_trip_id(trip.id)
        active_admins = [m for m in admin_members if m.is_active() and m.user_id != owner_member.user_id]
        
        if not active_admins:
            raise ValidationError(
                "Como propietario, debes transferir la propiedad a otro admin antes de abandonar el viaje"
            )

    async def validate_trip_access(self, trip_id: str, user_id: str) -> TripMember:
        """Validar que el usuario tenga acceso al viaje"""
        trip = await self._trip_repository.find_by_id(trip_id)
        if not trip or not trip.is_active():
            raise NotFoundError("Viaje no encontrado")
        
        member = await self._trip_member_repository.find_by_trip_and_user(trip_id, user_id)
        if not member or not member.is_active():
            raise ForbiddenError("No tienes acceso a este viaje")
        
        return member

    async def validate_trip_edit_permission(self, trip_id: str, user_id: str) -> TripMember:
        """Validar permisos de edición en el viaje"""
        member = await self.validate_trip_access(trip_id, user_id)
        
        if not member.can_edit_trip():
            raise ForbiddenError("No tienes permisos para editar este viaje")
        
        return member

    async def can_user_access_trip(self, trip_id: str, user_id: str) -> bool:
        """Verificar si un usuario puede acceder a un viaje"""
        try:
            await self.validate_trip_access(trip_id, user_id)
            return True
        except (NotFoundError, ForbiddenError):
            return False

    async def get_user_role_in_trip(self, trip_id: str, user_id: str) -> Optional[TripMemberRole]:
        """Obtener el rol del usuario en el viaje"""
        member = await self._trip_member_repository.find_by_trip_and_user(trip_id, user_id)
        if member and member.is_active():
            return TripMemberRole(member.role)
        return None

    async def count_active_members(self, trip_id: str) -> int:
        """Contar miembros activos del viaje"""
        members = await self._trip_member_repository.find_active_members_by_trip_id(trip_id)
        return len(members)

    async def validate_trip_deletion(self, trip: Trip, user_id: str):
        """Validar eliminación de viaje"""
        member = await self._trip_member_repository.find_by_trip_and_user(trip.id, user_id)
        if not member or not member.is_owner():
            raise ForbiddenError("Solo el propietario puede eliminar el viaje")
        
        if trip.status == TripStatus.ACTIVE.value:
            raise ValidationError("No se puede eliminar un viaje activo")

    async def validate_status_change(self, trip: Trip, new_status: TripStatus, user_id: str):
        """Validar cambio de estado del viaje"""
        member = await self._trip_member_repository.find_by_trip_and_user(trip.id, user_id)
        if not member or not member.can_edit_trip():
            raise ForbiddenError("No tienes permisos para cambiar el estado del viaje")
        
        current_status = TripStatus(trip.status)
        
        # Validar transiciones de estado válidas
        valid_transitions = {
            TripStatus.PLANNED: [TripStatus.ACTIVE, TripStatus.CANCELLED],
            TripStatus.ACTIVE: [TripStatus.COMPLETED, TripStatus.CANCELLED],
            TripStatus.COMPLETED: [],  # Estado final
            TripStatus.CANCELLED: [TripStatus.PLANNED]  # Solo si se reactiva
        }
        
        if new_status not in valid_transitions.get(current_status, []):
            raise ValidationError(f"No se puede cambiar de {current_status.value} a {new_status.value}")
        
        # Validaciones específicas por estado
        if new_status == TripStatus.ACTIVE:
            if trip.start_date > datetime.utcnow():
                raise ValidationError("No se puede activar un viaje antes de su fecha de inicio")
        
        elif new_status == TripStatus.COMPLETED:
            if trip.end_date > datetime.utcnow():
                raise ValidationError("No se puede completar un viaje antes de su fecha de fin")