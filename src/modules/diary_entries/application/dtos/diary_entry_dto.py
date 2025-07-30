from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class CreateDiaryEntryDTO(BaseModel):
    day_id: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    emotions: Optional[List[str]] = None


class UpdateDiaryEntryDTO(BaseModel):
    content: Optional[str] = None
    emotions: Optional[List[str]] = None


class AddEmotionDTO(BaseModel):
    emotion: str = Field(..., min_length=1)


class DiaryEntryResponseDTO(BaseModel):
    id: str
    day_id: str
    user_id: str
    content: str
    emotions: Optional[List[str]] = None
    word_count: int
    dominant_emotion: Optional[str] = None
    can_edit: bool
    can_delete: bool
    author_info: Optional[Dict[str, Any]] = None
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


class DiaryEntryStatsDTO(BaseModel):
    total_entries: int
    total_words: int
    average_words_per_entry: float
    most_common_emotion: Optional[str] = None
    entries_with_emotions: int
    entries_by_day: Dict[str, int]
    emotion_distribution: Dict[str, int]


class DiaryEntryDTOMapper:
    @staticmethod
    def to_diary_entry_response(
        entry_data: Dict[str, Any],
        can_edit: bool = False,
        can_delete: bool = False,
        author_info: Optional[Dict[str, Any]] = None,
        word_count: int = 0,
        dominant_emotion: Optional[str] = None
    ) -> DiaryEntryResponseDTO:
        return DiaryEntryResponseDTO(
            id=entry_data["id"],
            day_id=entry_data["day_id"],
            user_id=entry_data["user_id"],
            content=entry_data["content"],
            emotions=entry_data.get("emotions"),
            word_count=word_count,
            dominant_emotion=dominant_emotion,
            can_edit=can_edit,
            can_delete=can_delete,
            author_info=author_info,
            is_deleted=entry_data.get("is_deleted", False),
            created_at=entry_data["created_at"],
            updated_at=entry_data["updated_at"]
        )

    @staticmethod
    def to_diary_entries_list(
        entries_data: List[Dict[str, Any]],
        user_permissions: Dict[str, Dict[str, bool]] = None,
        authors_info: Dict[str, Dict[str, Any]] = None
    ) -> List[DiaryEntryResponseDTO]:
        return [
            DiaryEntryDTOMapper.to_diary_entry_response(
                entry_data,
                can_edit=user_permissions.get(entry_data["id"], {}).get("can_edit", False),
                can_delete=user_permissions.get(entry_data["id"], {}).get("can_delete", False),
                author_info=authors_info.get(entry_data["user_id"]),
                word_count=len(entry_data["content"].split()) if entry_data["content"] else 0
            )
            for entry_data in entries_data
        ]