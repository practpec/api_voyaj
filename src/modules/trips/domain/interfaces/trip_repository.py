from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..trip import Trip


class ITripRepository(ABC):
    
    @abstractmethod
    async def create(self, trip: Trip) -> Trip:
        pass

    @abstractmethod
    async def find_by_id(self, trip_id: str) -> Optional[Trip]:
        pass

    @abstractmethod
    async def update(self, trip: Trip) -> Trip:
        pass

    @abstractmethod
    async def delete(self, trip_id: str) -> bool:
        pass

    @abstractmethod
    async def find_by_owner_id(
        self, 
        owner_id: str, 
        page: int = 1, 
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> tuple[List[Trip], int]:
        pass

    @abstractmethod
    async def find_active_by_owner_id(self, owner_id: str) -> List[Trip]:
        pass

    @abstractmethod
    async def find_by_destination(
        self, 
        destination: str, 
        user_id: Optional[str] = None
    ) -> List[Trip]:
        pass

    @abstractmethod
    async def find_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        user_id: Optional[str] = None
    ) -> List[Trip]:
        pass

    @abstractmethod
    async def find_by_category(
        self, 
        category: str, 
        user_id: Optional[str] = None
    ) -> List[Trip]:
        pass

    @abstractmethod
    async def find_group_trips_by_user(self, user_id: str) -> List[Trip]:
        pass

    @abstractmethod
    async def search(
        self, 
        query: str, 
        user_id: Optional[str] = None
    ) -> List[Trip]:
        pass

    @abstractmethod
    async def find_with_filters(
        self, 
        filters: Dict[str, Any], 
        page: int = 1, 
        limit: int = 20
    ) -> tuple[List[Trip], int]:
        pass

    @abstractmethod
    async def count_by_filters(self, filters: Dict[str, Any]) -> int:
        pass

    @abstractmethod
    async def exists_by_id(self, trip_id: str) -> bool:
        pass

    @abstractmethod
    async def is_owner(self, trip_id: str, user_id: str) -> bool:
        pass

    @abstractmethod
    async def get_user_trip_stats(self, user_id: str) -> Dict[str, Any]:
        pass