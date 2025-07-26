# src/modules/activity_votes/domain/activity_vote.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import uuid
from shared.errors.custom_errors import ValidationError


@dataclass
class ActivityVoteData:
    """Datos del voto de actividad"""
    id: str
    activity_id: str
    user_id: str
    trip_id: str
    vote_type: str  # 'up', 'down', 'neutral'
    created_at: datetime
    updated_at: datetime
    is_deleted: bool = False


class ActivityVote:
    """Entidad de dominio para votos de actividades"""
    
    VALID_VOTE_TYPES = ['up', 'down', 'neutral']

    def __init__(self, data: ActivityVoteData):
        self._data = data
        self._validate()

    @classmethod
    def create(
        cls,
        activity_id: str,
        user_id: str,
        trip_id: str,
        vote_type: str
    ) -> 'ActivityVote':
        """Crear nuevo voto de actividad"""
        now = datetime.utcnow()
        
        data = ActivityVoteData(
            id=str(uuid.uuid4()),
            activity_id=activity_id,
            user_id=user_id,
            trip_id=trip_id,
            vote_type=vote_type,
            created_at=now,
            updated_at=now,
            is_deleted=False
        )
        
        return cls(data)

    @classmethod
    def from_dict(cls, data: dict) -> 'ActivityVote':
        """Crear desde diccionario"""
        vote_data = ActivityVoteData(
            id=data['id'],
            activity_id=data['activity_id'],
            user_id=data['user_id'],
            trip_id=data['trip_id'],
            vote_type=data['vote_type'],
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            is_deleted=data.get('is_deleted', False)
        )
        return cls(vote_data)

    def _validate(self):
        """Validar datos del voto"""
        if not self._data.activity_id:
            raise ValidationError("ID de actividad es requerido")
        
        if not self._data.user_id:
            raise ValidationError("ID de usuario es requerido")
        
        if not self._data.trip_id:
            raise ValidationError("ID de viaje es requerido")
            
        if self._data.vote_type not in self.VALID_VOTE_TYPES:
            raise ValidationError(f"Tipo de voto debe ser uno de: {', '.join(self.VALID_VOTE_TYPES)}")

    @property
    def id(self) -> str:
        return self._data.id

    @property
    def activity_id(self) -> str:
        return self._data.activity_id

    @property
    def user_id(self) -> str:
        return self._data.user_id

    @property
    def trip_id(self) -> str:
        return self._data.trip_id

    @property
    def vote_type(self) -> str:
        return self._data.vote_type

    @property
    def created_at(self) -> datetime:
        return self._data.created_at

    @property
    def updated_at(self) -> datetime:
        return self._data.updated_at

    def change_vote_type(self, new_vote_type: str) -> None:
        """Cambiar tipo de voto"""
        if new_vote_type not in self.VALID_VOTE_TYPES:
            raise ValidationError(f"Tipo de voto debe ser uno de: {', '.join(self.VALID_VOTE_TYPES)}")
        
        self._data.vote_type = new_vote_type
        self._data.updated_at = datetime.utcnow()

    def soft_delete(self) -> None:
        """Eliminación suave del voto"""
        self._data.is_deleted = True
        self._data.updated_at = datetime.utcnow()

    def restore(self) -> None:
        """Restaurar voto eliminado"""
        self._data.is_deleted = False
        self._data.updated_at = datetime.utcnow()

    def is_active(self) -> bool:
        """Verificar si el voto está activo"""
        return not self._data.is_deleted

    def is_positive(self) -> bool:
        """Verificar si es voto positivo"""
        return self._data.vote_type == 'up'

    def is_negative(self) -> bool:
        """Verificar si es voto negativo"""
        return self._data.vote_type == 'down'

    def is_neutral(self) -> bool:
        """Verificar si es voto neutral"""
        return self._data.vote_type == 'neutral'

    def to_public_data(self) -> ActivityVoteData:
        """Obtener datos públicos del voto"""
        return self._data

    def to_dict(self) -> dict:
        """Convertir a diccionario"""
        return {
            'id': self._data.id,
            'activity_id': self._data.activity_id,
            'user_id': self._data.user_id,
            'trip_id': self._data.trip_id,
            'vote_type': self._data.vote_type,
            'created_at': self._data.created_at,
            'updated_at': self._data.updated_at,
            'is_deleted': self._data.is_deleted
        }