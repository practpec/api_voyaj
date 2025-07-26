# src/modules/diary_recommendations/domain/diary_recommendation.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class RecommendationType(Enum):
    PLACE = "place"
    ACTIVITY = "activity"
    RESTAURANT = "restaurant"
    EXPERIENCE = "experience"
    TIP = "tip"
    WARNING = "warning"
    GENERAL = "general"


@dataclass
class DiaryRecommendationData:
    id: str
    diary_entry_id: str
    note: str
    type: RecommendationType
    is_deleted: bool = False
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()


class DiaryRecommendation:
    def __init__(self, data: DiaryRecommendationData):
        self._data = data

    @property
    def id(self) -> str:
        return self._data.id

    @property
    def diary_entry_id(self) -> str:
        return self._data.diary_entry_id

    @property
    def note(self) -> str:
        return self._data.note

    @property
    def type(self) -> RecommendationType:
        return self._data.type

    @property
    def is_deleted(self) -> bool:
        return self._data.is_deleted

    @property
    def created_at(self) -> datetime:
        return self._data.created_at

    @property
    def updated_at(self) -> datetime:
        return self._data.updated_at

    def update_note(self, note: str) -> None:
        """Actualizar nota de la recomendación"""
        self._data.note = note
        self._data.updated_at = datetime.utcnow()

    def update_type(self, recommendation_type: RecommendationType) -> None:
        """Actualizar tipo de recomendación"""
        self._data.type = recommendation_type
        self._data.updated_at = datetime.utcnow()

    def mark_as_deleted(self) -> None:
        """Marcar como eliminada"""
        self._data.is_deleted = True
        self._data.updated_at = datetime.utcnow()

    def restore(self) -> None:
        """Restaurar recomendación"""
        self._data.is_deleted = False
        self._data.updated_at = datetime.utcnow()

    def to_public_data(self) -> DiaryRecommendationData:
        """Obtener datos públicos de la recomendación"""
        return self._data

    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return {
            "id": self.id,
            "diary_entry_id": self.diary_entry_id,
            "note": self.note,
            "type": self.type.value,
            "is_deleted": self.is_deleted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }