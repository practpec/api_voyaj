from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..diary_entry import DiaryEntry


class IDiaryEntryRepository(ABC):

    @abstractmethod
    async def create(self, diary_entry: DiaryEntry) -> DiaryEntry:
        pass

    @abstractmethod
    async def find_by_id(self, entry_id: str) -> Optional[DiaryEntry]:
        pass

    @abstractmethod
    async def update(self, diary_entry: DiaryEntry) -> DiaryEntry:
        pass

    @abstractmethod
    async def delete(self, entry_id: str) -> bool:
        pass

    @abstractmethod
    async def find_by_day_id(self, day_id: str) -> List[DiaryEntry]:
        pass

    @abstractmethod
    async def find_by_user_id(self, user_id: str) -> List[DiaryEntry]:
        pass

    @abstractmethod
    async def find_by_trip_id(self, trip_id: str) -> List[DiaryEntry]:
        pass

    @abstractmethod
    async def find_by_user_and_day(self, user_id: str, day_id: str) -> Optional[DiaryEntry]:
        pass

    @abstractmethod
    async def count_by_day_id(self, day_id: str) -> int:
        pass

    @abstractmethod
    async def count_by_user_id(self, user_id: str) -> int:
        pass

    @abstractmethod
    async def count_by_trip_id(self, trip_id: str) -> int:
        pass

    @abstractmethod
    async def count_by_user_and_trip(self, user_id: str, trip_id: str) -> int:
        pass

    @abstractmethod
    async def get_user_diary_statistics(self, user_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def get_trip_diary_statistics(self, trip_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def find_entries_with_emotions(self, trip_id: str) -> List[DiaryEntry]:
        pass

    @abstractmethod
    async def find_entries_by_emotion_type(self, emotion_type: str, trip_id: Optional[str] = None) -> List[DiaryEntry]:
        pass

    @abstractmethod
    async def get_most_active_writers(self, trip_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get_emotion_trends_by_trip(self, trip_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def find_entries_by_date_range(
        self, 
        trip_id: str, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> List[DiaryEntry]:
        pass