from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
import uuid
from enum import Enum
from shared.errors.custom_errors import ValidationError


class MoodType(Enum):
    VERY_HAPPY = "very_happy"
    HAPPY = "happy"
    NEUTRAL = "neutral"
    SAD = "sad"
    VERY_SAD = "very_sad"
    EXCITED = "excited"
    TIRED = "tired"
    RELAXED = "relaxed"
    ADVENTUROUS = "adventurous"
    NOSTALGIC = "nostalgic"


@dataclass
class DiaryEntryData:
    id: str
    day_id: str
    user_id: str
    content: str
    emotions: Optional[Dict[str, Any]]
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


class DiaryEntry:
    def __init__(self, data: DiaryEntryData):
        self._data = data
        self._validate()

    @classmethod
    def create(
        cls,
        day_id: str,
        user_id: str,
        content: str,
        emotions: Optional[Dict[str, Any]] = None
    ) -> 'DiaryEntry':
        """Crear nueva entrada de diario"""
        if not content or len(content.strip()) < 10:
            raise ValidationError("El contenido debe tener al menos 10 caracteres")

        if len(content) > 5000:
            raise ValidationError("El contenido no puede exceder 5000 caracteres")

        # Validar estructura de emociones
        validated_emotions = cls._validate_emotions(emotions) if emotions else None

        data = DiaryEntryData(
            id=str(uuid.uuid4()),
            day_id=day_id,
            user_id=user_id,
            content=content.strip(),
            emotions=validated_emotions,
            is_deleted=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        return cls(data)

    def update_content(self, new_content: str) -> None:
        """Actualizar contenido de la entrada"""
        if not new_content or len(new_content.strip()) < 10:
            raise ValidationError("El contenido debe tener al menos 10 caracteres")

        if len(new_content) > 5000:
            raise ValidationError("El contenido no puede exceder 5000 caracteres")

        self._data.content = new_content.strip()
        self._data.updated_at = datetime.utcnow()

    def update_emotions(self, emotions: Dict[str, Any]) -> None:
        """Actualizar emociones de la entrada"""
        validated_emotions = self._validate_emotions(emotions)
        self._data.emotions = validated_emotions
        self._data.updated_at = datetime.utcnow()

    def add_emotion(self, emotion_type: str, intensity: int, note: Optional[str] = None) -> None:
        """Agregar nueva emoción"""
        if not self._data.emotions:
            self._data.emotions = {"emotions": []}

        if emotion_type not in [e.value for e in MoodType]:
            raise ValidationError(f"Tipo de emoción '{emotion_type}' no válido")

        if not 1 <= intensity <= 5:
            raise ValidationError("La intensidad debe estar entre 1 y 5")

        emotion_entry = {
            "type": emotion_type,
            "intensity": intensity,
            "note": note,
            "added_at": datetime.utcnow().isoformat()
        }

        # Remover emoción existente del mismo tipo
        if "emotions" not in self._data.emotions:
            self._data.emotions["emotions"] = []

        self._data.emotions["emotions"] = [
            e for e in self._data.emotions["emotions"] 
            if e.get("type") != emotion_type
        ]

        self._data.emotions["emotions"].append(emotion_entry)
        self._data.updated_at = datetime.utcnow()

    def remove_emotion(self, emotion_type: str) -> None:
        """Remover emoción específica"""
        if not self._data.emotions or "emotions" not in self._data.emotions:
            return

        self._data.emotions["emotions"] = [
            e for e in self._data.emotions["emotions"] 
            if e.get("type") != emotion_type
        ]

        self._data.updated_at = datetime.utcnow()

    def soft_delete(self) -> None:
        """Eliminación suave de la entrada"""
        self._data.is_deleted = True
        self._data.updated_at = datetime.utcnow()

    def restore(self) -> None:
        """Restaurar entrada eliminada"""
        self._data.is_deleted = False
        self._data.updated_at = datetime.utcnow()

    def is_active(self) -> bool:
        """Verificar si la entrada está activa"""
        return not self._data.is_deleted

    def can_be_edited_by(self, user_id: str) -> bool:
        """Verificar si el usuario puede editar la entrada"""
        return self._data.user_id == user_id and self.is_active()

    def get_word_count(self) -> int:
        """Obtener conteo de palabras"""
        return len(self._data.content.split())

    def get_dominant_emotion(self) -> Optional[str]:
        """Obtener la emoción dominante (mayor intensidad)"""
        if not self._data.emotions or "emotions" not in self._data.emotions:
            return None

        emotions = self._data.emotions["emotions"]
        if not emotions:
            return None

        dominant = max(emotions, key=lambda x: x.get("intensity", 0))
        return dominant.get("type")

    def to_public_data(self) -> DiaryEntryData:
        """Obtener datos públicos de la entrada"""
        return self._data

    @staticmethod
    def _validate_emotions(emotions: Dict[str, Any]) -> Dict[str, Any]:
        """Validar estructura de emociones"""
        if not isinstance(emotions, dict):
            raise ValidationError("Las emociones deben ser un objeto")

        # Estructura esperada: {"emotions": [{"type": str, "intensity": int, "note": str}]}
        if "emotions" in emotions:
            if not isinstance(emotions["emotions"], list):
                raise ValidationError("Las emociones deben ser una lista")

            for emotion in emotions["emotions"]:
                if not isinstance(emotion, dict):
                    raise ValidationError("Cada emoción debe ser un objeto")

                if "type" not in emotion or "intensity" not in emotion:
                    raise ValidationError("Cada emoción debe tener tipo e intensidad")

                if emotion["type"] not in [e.value for e in MoodType]:
                    raise ValidationError(f"Tipo de emoción '{emotion['type']}' no válido")

                if not isinstance(emotion["intensity"], int) or not 1 <= emotion["intensity"] <= 5:
                    raise ValidationError("La intensidad debe ser un entero entre 1 y 5")

        return emotions

    def _validate(self) -> None:
        """Validar datos de la entrada"""
        if not self._data.day_id:
            raise ValidationError("ID del día es requerido")

        if not self._data.user_id:
            raise ValidationError("ID del usuario es requerido")

        if not self._data.content:
            raise ValidationError("El contenido es requerido")

    @property
    def id(self) -> str:
        return self._data.id

    @property
    def day_id(self) -> str:
        return self._data.day_id

    @property
    def user_id(self) -> str:
        return self._data.user_id

    @property
    def content(self) -> str:
        return self._data.content

    @property
    def emotions(self) -> Optional[Dict[str, Any]]:
        return self._data.emotions

    @property
    def created_at(self) -> datetime:
        return self._data.created_at

    @property
    def updated_at(self) -> datetime:
        return self._data.updated_at