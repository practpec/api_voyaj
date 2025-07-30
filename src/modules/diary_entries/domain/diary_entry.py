from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass
from collections import Counter
import uuid


@dataclass
class DiaryEntryData:
    id: str
    day_id: str
    user_id: str
    content: str
    emotions: Optional[List[str]] = None
    is_deleted: bool = False
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()


class DiaryEntry:
    def __init__(self, data: DiaryEntryData):
        self._data = data

    @classmethod
    def create(
        cls,
        day_id: str,
        user_id: str,
        content: str,
        emotions: Optional[List[str]] = None
    ) -> 'DiaryEntry':
        data = DiaryEntryData(
            id=str(uuid.uuid4()),
            day_id=day_id,
            user_id=user_id,
            content=content,
            emotions=emotions or []
        )
        return cls(data)

    @classmethod
    def from_data(cls, data: Dict[str, Any]) -> 'DiaryEntry':
        return cls(DiaryEntryData(
            id=data["id"],
            day_id=data["day_id"],
            user_id=data["user_id"],
            content=data["content"],
            emotions=data.get("emotions", []),
            is_deleted=data.get("is_deleted", False),
            created_at=data["created_at"],
            updated_at=data["updated_at"]
        ))

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
    def emotions(self) -> Optional[List[str]]:
        return self._data.emotions

    @property
    def is_deleted(self) -> bool:
        return self._data.is_deleted

    @property
    def created_at(self) -> datetime:
        return self._data.created_at

    @property
    def updated_at(self) -> datetime:
        return self._data.updated_at

    def update_content(self, content: str) -> None:
        if not content or not content.strip():
            raise ValueError("El contenido no puede estar vacío")
        
        self._data.content = content.strip()
        self._mark_as_updated()

    def update_emotions(self, emotions: List[str]) -> None:
        self._data.emotions = emotions or []
        self._mark_as_updated()

    def add_emotion(self, emotion: str) -> None:
        if not emotion or not emotion.strip():
            raise ValueError("La emoción no puede estar vacía")
        
        emotion = emotion.strip().lower()
        
        if self._data.emotions is None:
            self._data.emotions = []
        
        if emotion not in self._data.emotions:
            self._data.emotions.append(emotion)
            self._mark_as_updated()

    def remove_emotion(self, emotion: str) -> None:
        if self._data.emotions and emotion in self._data.emotions:
            self._data.emotions.remove(emotion)
            self._mark_as_updated()

    def get_word_count(self) -> int:
        if not self._data.content:
            return 0
        return len(self._data.content.split())

    def get_dominant_emotion(self) -> Optional[str]:
        if not self._data.emotions or len(self._data.emotions) == 0:
            return None
        
        emotion_counts = Counter(self._data.emotions)
        return emotion_counts.most_common(1)[0][0]

    def has_emotion(self, emotion: str) -> bool:
        return self._data.emotions is not None and emotion.lower() in self._data.emotions

    def is_active(self) -> bool:
        return not self._data.is_deleted

    def soft_delete(self) -> None:
        self._data.is_deleted = True
        self._mark_as_updated()

    def restore(self) -> None:
        self._data.is_deleted = False
        self._mark_as_updated()

    def _mark_as_updated(self) -> None:
        self._data.updated_at = datetime.utcnow()

    def to_public_data(self) -> Dict[str, Any]:
        return {
            "id": self._data.id,
            "day_id": self._data.day_id,
            "user_id": self._data.user_id,
            "content": self._data.content,
            "emotions": self._data.emotions,
            "is_deleted": self._data.is_deleted,
            "created_at": self._data.created_at,
            "updated_at": self._data.updated_at
        }