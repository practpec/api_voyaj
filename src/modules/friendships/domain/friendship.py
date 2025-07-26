from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import uuid4

from shared.constants import FRIENDSHIP_STATUS


@dataclass
class FriendshipData:
    id: str
    user_id: str
    friend_id: str
    status: str
    created_at: datetime
    accepted_at: Optional[datetime] = None
    is_deleted: bool = False


class Friendship:
    def __init__(
        self,
        id: str,
        user_id: str,
        friend_id: str,
        status: str,
        created_at: datetime,
        accepted_at: Optional[datetime] = None,
        is_deleted: bool = False
    ):
        self._id = id
        self._user_id = user_id
        self._friend_id = friend_id
        self._status = status
        self._created_at = created_at
        self._accepted_at = accepted_at
        self._is_deleted = is_deleted

    @classmethod
    def create(cls, user_id: str, friend_id: str) -> 'Friendship':
        """Crear nueva solicitud de amistad"""
        if user_id == friend_id:
            raise ValueError("No puedes enviarte una solicitud de amistad a ti mismo")

        return cls(
            id=str(uuid4()),
            user_id=user_id,
            friend_id=friend_id,
            status=FRIENDSHIP_STATUS["PENDING"],
            created_at=datetime.utcnow(),
            accepted_at=None,
            is_deleted=False
        )

    @classmethod
    def from_data(cls, data: FriendshipData) -> 'Friendship':
        """Crear instancia desde datos"""
        return cls(
            id=data.id,
            user_id=data.user_id,
            friend_id=data.friend_id,
            status=data.status,
            created_at=data.created_at,
            accepted_at=data.accepted_at,
            is_deleted=data.is_deleted
        )

    def accept(self) -> None:
        """Aceptar solicitud de amistad"""
        if self._status != FRIENDSHIP_STATUS["PENDING"]:
            raise ValueError("Solo se pueden aceptar solicitudes pendientes")
        
        self._status = FRIENDSHIP_STATUS["ACCEPTED"]
        self._accepted_at = datetime.utcnow()

    def reject(self) -> None:
        """Rechazar solicitud de amistad"""
        if self._status != FRIENDSHIP_STATUS["PENDING"]:
            raise ValueError("Solo se pueden rechazar solicitudes pendientes")
        
        self._status = FRIENDSHIP_STATUS["REJECTED"]

    def remove(self) -> None:
        """Eliminar amistad (soft delete)"""
        self._is_deleted = True

    def restore(self) -> None:
        """Restaurar amistad"""
        self._is_deleted = False

    # Getters
    @property
    def id(self) -> str:
        return self._id

    @property
    def user_id(self) -> str:
        return self._user_id

    @property
    def friend_id(self) -> str:
        return self._friend_id

    @property
    def status(self) -> str:
        return self._status

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def accepted_at(self) -> Optional[datetime]:
        return self._accepted_at

    @property
    def is_deleted(self) -> bool:
        return self._is_deleted

    def is_pending(self) -> bool:
        """Verificar si la solicitud está pendiente"""
        return self._status == FRIENDSHIP_STATUS["PENDING"]

    def is_accepted(self) -> bool:
        """Verificar si la amistad está aceptada"""
        return self._status == FRIENDSHIP_STATUS["ACCEPTED"]

    def is_rejected(self) -> bool:
        """Verificar si la solicitud fue rechazada"""
        return self._status == FRIENDSHIP_STATUS["REJECTED"]

    def to_data(self) -> FriendshipData:
        """Convertir a datos para persistencia"""
        return FriendshipData(
            id=self._id,
            user_id=self._user_id,
            friend_id=self._friend_id,
            status=self._status,
            created_at=self._created_at,
            accepted_at=self._accepted_at,
            is_deleted=self._is_deleted
        )

    def to_public_data(self) -> FriendshipData:
        """Convertir a datos públicos"""
        return self.to_data()