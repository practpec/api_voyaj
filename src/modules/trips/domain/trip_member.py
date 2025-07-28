# src/modules/trips/domain/trip_member.py
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4


class TripMemberRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class TripMemberStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    LEFT = "left"
    REMOVED = "removed"


@dataclass
class TripMemberData:
    id: str
    trip_id: str
    user_id: str
    role: str
    status: str
    notes: Optional[str]
    invited_by: Optional[str]
    invited_at: datetime
    joined_at: Optional[datetime]
    left_at: Optional[datetime]
    is_deleted: bool = False


class TripMember:
    def __init__(
        self,
        id: str,
        trip_id: str,
        user_id: str,
        role: str,
        status: str,
        notes: Optional[str],
        invited_by: Optional[str],
        invited_at: datetime,
        joined_at: Optional[datetime],
        left_at: Optional[datetime],
        is_deleted: bool = False
    ):
        self._id = id
        self._trip_id = trip_id
        self._user_id = user_id
        self._role = role
        self._status = status
        self._notes = notes
        self._invited_by = invited_by
        self._invited_at = invited_at
        self._joined_at = joined_at
        self._left_at = left_at
        self._is_deleted = is_deleted

    @classmethod
    def create_owner(cls, trip_id: str, user_id: str) -> 'TripMember':
        return cls(
            id=str(uuid4()),
            trip_id=trip_id,
            user_id=user_id,
            role=TripMemberRole.OWNER.value,
            status=TripMemberStatus.ACCEPTED.value,
            notes=None,
            invited_by=None,
            invited_at=datetime.utcnow(),
            joined_at=datetime.utcnow(),
            left_at=None,
            is_deleted=False
        )

    @classmethod
    def create_invitation(
        cls,
        trip_id: str,
        user_id: str,
        invited_by: str,
        role: TripMemberRole = TripMemberRole.MEMBER,
        notes: Optional[str] = None
    ) -> 'TripMember':
        return cls(
            id=str(uuid4()),
            trip_id=trip_id,
            user_id=user_id,
            role=role.value,
            status=TripMemberStatus.PENDING.value,
            notes=notes,
            invited_by=invited_by,
            invited_at=datetime.utcnow(),
            joined_at=None,
            left_at=None,
            is_deleted=False
        )

    @classmethod
    def from_data(cls, data: TripMemberData) -> 'TripMember':
        return cls(
            id=data.id,
            trip_id=data.trip_id,
            user_id=data.user_id,
            role=data.role,
            status=data.status,
            notes=data.notes,
            invited_by=data.invited_by,
            invited_at=data.invited_at,
            joined_at=data.joined_at,
            left_at=data.left_at,
            is_deleted=data.is_deleted
        )

    def accept_invitation(self):
        """Aceptar invitación al viaje"""
        if self._status != TripMemberStatus.PENDING.value:
            raise ValueError("Solo se pueden aceptar invitaciones pendientes")
        
        self._status = TripMemberStatus.ACCEPTED.value
        self._joined_at = datetime.utcnow()

    def reject_invitation(self):
        """Rechazar invitación al viaje"""
        if self._status != TripMemberStatus.PENDING.value:
            raise ValueError("Solo se pueden rechazar invitaciones pendientes")
        
        self._status = TripMemberStatus.REJECTED.value

    def leave_trip(self):
        """Abandonar el viaje"""
        if self._status != TripMemberStatus.ACCEPTED.value:
            raise ValueError("Solo los miembros aceptados pueden abandonar el viaje")
        
        if self._role == TripMemberRole.OWNER.value:
            raise ValueError("El propietario no puede abandonar el viaje")
        
        self._status = TripMemberStatus.LEFT.value
        self._left_at = datetime.utcnow()

    def remove_from_trip(self):
        """Remover del viaje (por admin/owner)"""
        if self._role == TripMemberRole.OWNER.value:
            raise ValueError("El propietario no puede ser removido del viaje")
        
        self._status = TripMemberStatus.REMOVED.value
        self._left_at = datetime.utcnow()

    def change_role(self, new_role: TripMemberRole):
        """Cambiar rol del miembro"""
        if self._role == TripMemberRole.OWNER.value:
            raise ValueError("No se puede cambiar el rol del propietario")
        
        self._role = new_role.value

    def update_notes(self, notes: Optional[str]):
        """Actualizar notas privadas"""
        self._notes = notes

    def soft_delete(self):
        """Marcar como eliminado"""
        self._is_deleted = True

    def restore(self):
        """Restaurar (deshacer eliminación)"""
        self._is_deleted = False

    def is_active(self) -> bool:
        """Verificar si el miembro está activo"""
        return not self._is_deleted and self._status == TripMemberStatus.ACCEPTED.value

    def is_owner(self) -> bool:
        """Verificar si es propietario"""
        return self._role == TripMemberRole.OWNER.value

    def is_admin(self) -> bool:
        """Verificar si es administrador o propietario"""
        return self._role in [TripMemberRole.OWNER.value, TripMemberRole.ADMIN.value]

    def can_edit_trip(self) -> bool:
        """Verificar si puede editar el viaje"""
        return self._role in [TripMemberRole.OWNER.value, TripMemberRole.ADMIN.value]

    def can_invite_members(self) -> bool:
        """Verificar si puede invitar miembros"""
        return self._role in [TripMemberRole.OWNER.value, TripMemberRole.ADMIN.value]

    def to_public_data(self) -> TripMemberData:
        """Convertir a datos públicos"""
        return TripMemberData(
            id=self._id,
            trip_id=self._trip_id,
            user_id=self._user_id,
            role=self._role,
            status=self._status,
            notes=self._notes,
            invited_by=self._invited_by,
            invited_at=self._invited_at,
            joined_at=self._joined_at,
            left_at=self._left_at,
            is_deleted=self._is_deleted
        )

    # =====================================================
    # PROPIEDADES PÚBLICAS (GETTERS)
    # =====================================================
    
    @property
    def id(self) -> str:
        return self._id

    @property
    def trip_id(self) -> str:
        return self._trip_id

    @property
    def user_id(self) -> str:
        return self._user_id

    @property
    def role(self) -> str:
        return self._role

    @property
    def status(self) -> str:
        return self._status

    @property
    def notes(self) -> Optional[str]:
        return self._notes

    @property
    def invited_by(self) -> Optional[str]:
        return self._invited_by

    @property
    def invited_at(self) -> datetime:
        return self._invited_at

    @property
    def joined_at(self) -> Optional[datetime]:
        return self._joined_at

    @property
    def left_at(self) -> Optional[datetime]:
        return self._left_at

    @property
    def is_deleted(self) -> bool:
        return self._is_deleted