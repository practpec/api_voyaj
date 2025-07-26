from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List
from ...domain.diary_entry import DiaryEntryData, MoodType


@dataclass
class CreateDiaryEntryDTO:
    day_id: str
    content: str
    emotions: Optional[Dict[str, Any]] = None


@dataclass
class UpdateDiaryEntryDTO:
    content: Optional[str] = None
    emotions: Optional[Dict[str, Any]] = None


@dataclass
class AddEmotionDTO:
    emotion_type: str
    intensity: int
    note: Optional[str] = None


@dataclass
class DiaryEntryResponseDTO:
    id: str
    day_id: str
    user_id: str
    content: str
    emotions: Optional[Dict[str, Any]]
    word_count: int
    dominant_emotion: Optional[str]
    can_edit: bool
    can_delete: bool
    created_at: datetime
    updated_at: datetime
    author_info: Optional[Dict[str, Any]] = None


@dataclass
class DiaryEntryListResponseDTO:
    id: str
    day_id: str
    user_id: str
    content_preview: str  # Primeros 100 caracteres
    word_count: int
    dominant_emotion: Optional[str]
    has_emotions: bool
    can_edit: bool
    created_at: datetime
    updated_at: datetime
    author_info: Optional[Dict[str, Any]] = None


@dataclass
class DayDiaryEntriesResponseDTO:
    day_id: str
    day_date: str
    entries: List[DiaryEntryListResponseDTO]
    total_entries: int
    total_words: int
    entries_with_emotions: int
    emotion_distribution: Dict[str, int]


@dataclass
class TripDiaryStatsDTO:
    trip_id: str
    total_entries: int
    total_words: int
    active_contributors: int
    entries_with_emotions: int
    most_common_emotion: Optional[str]
    average_words_per_entry: float
    user_contributions: Dict[str, Dict[str, int]]
    emotion_trends: Dict[str, Any]


@dataclass
class EmotionSuggestionDTO:
    suggested_emotions: List[str]
    confidence_scores: Dict[str, float]


class DiaryEntryDTOMapper:
    
    MOOD_LABELS = {
        MoodType.VERY_HAPPY.value: "Muy Feliz",
        MoodType.HAPPY.value: "Feliz",
        MoodType.NEUTRAL.value: "Neutral",
        MoodType.SAD.value: "Triste",
        MoodType.VERY_SAD.value: "Muy Triste",
        MoodType.EXCITED.value: "Emocionado",
        MoodType.TIRED.value: "Cansado",
        MoodType.RELAXED.value: "Relajado",
        MoodType.ADVENTUROUS.value: "Aventurero",
        MoodType.NOSTALGIC.value: "Nostálgico"
    }

    @staticmethod
    def to_diary_entry_response(
        entry_data: DiaryEntryData,
        can_edit: bool = False,
        can_delete: bool = False,
        author_info: Optional[Dict[str, Any]] = None,
        word_count: int = 0,
        dominant_emotion: Optional[str] = None
    ) -> DiaryEntryResponseDTO:
        return DiaryEntryResponseDTO(
            id=entry_data.id,
            day_id=entry_data.day_id,
            user_id=entry_data.user_id,
            content=entry_data.content,
            emotions=entry_data.emotions,
            word_count=word_count,
            dominant_emotion=dominant_emotion,
            can_edit=can_edit,
            can_delete=can_delete,
            created_at=entry_data.created_at,
            updated_at=entry_data.updated_at,
            author_info=author_info
        )

    @staticmethod
    def to_diary_entry_list_response(
        entry_data: DiaryEntryData,
        can_edit: bool = False,
        author_info: Optional[Dict[str, Any]] = None,
        word_count: int = 0,
        dominant_emotion: Optional[str] = None
    ) -> DiaryEntryListResponseDTO:
        # Crear preview del contenido (primeros 100 caracteres)
        content_preview = (entry_data.content[:100] + "...") if len(entry_data.content) > 100 else entry_data.content
        
        return DiaryEntryListResponseDTO(
            id=entry_data.id,
            day_id=entry_data.day_id,
            user_id=entry_data.user_id,
            content_preview=content_preview,
            word_count=word_count,
            dominant_emotion=dominant_emotion,
            has_emotions=bool(entry_data.emotions and entry_data.emotions.get("emotions")),
            can_edit=can_edit,
            created_at=entry_data.created_at,
            updated_at=entry_data.updated_at,
            author_info=author_info
        )

    @staticmethod
    def to_day_diary_entries_response(
        day_id: str,
        day_date: str,
        entries: List[DiaryEntryListResponseDTO],
        stats: Dict[str, Any]
    ) -> DayDiaryEntriesResponseDTO:
        return DayDiaryEntriesResponseDTO(
            day_id=day_id,
            day_date=day_date,
            entries=entries,
            total_entries=stats.get("total_entries", 0),
            total_words=stats.get("total_words", 0),
            entries_with_emotions=stats.get("entries_with_emotions", 0),
            emotion_distribution=stats.get("emotion_distribution", {})
        )

    @staticmethod
    def to_trip_diary_stats(stats_data: Dict[str, Any]) -> TripDiaryStatsDTO:
        return TripDiaryStatsDTO(
            trip_id=stats_data.get("trip_id", ""),
            total_entries=stats_data.get("total_entries", 0),
            total_words=stats_data.get("total_words", 0),
            active_contributors=len(stats_data.get("user_contributions", {})),
            entries_with_emotions=stats_data.get("entries_with_emotions", 0),
            most_common_emotion=stats_data.get("most_common_emotion"),
            average_words_per_entry=stats_data.get("average_words_per_entry", 0.0),
            user_contributions=stats_data.get("user_contributions", {}),
            emotion_trends=stats_data.get("emotion_trends", {})
        )

    @staticmethod
    def to_emotion_suggestion(
        suggested_emotions: List[str],
        confidence_scores: Optional[Dict[str, float]] = None
    ) -> EmotionSuggestionDTO:
        return EmotionSuggestionDTO(
            suggested_emotions=suggested_emotions,
            confidence_scores=confidence_scores or {}
        )