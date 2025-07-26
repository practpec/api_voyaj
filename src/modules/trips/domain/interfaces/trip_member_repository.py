from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..trip_member import TripMember


class ITripMemberRepository(ABC):
    
    @abstractmethod
    async def create(self, trip_member: TripMember) -> TripMember:
        pass

    @abstractmethod
    async def find_by_id(self, member_id: str) -> Optional[TripMember]:
        pass

    @abstractmethod
    async def update(self, trip_member: TripMember) -> TripMember:
        pass

    @abstractmethod
    async def delete(self, member_id: str) -> bool:
        pass

    @abstractmethod
    async def find_by_trip_id(
        self, 
        trip_id: str, 
        page: int = 1, 
        limit: int = 50
    ) -> tuple[List[TripMember], int]:
        pass

    @abstractmethod
    async def find_active_members_by_trip_id(self, trip_id: str) -> List[TripMember]:
        pass

    @abstractmethod
    async def find_pending_members_by_trip_id(self, trip_id: str) -> List[TripMember]:
        pass

    @abstractmethod
    async def find_trip_owner(self, trip_id: str) -> Optional[TripMember]:
        pass

    @abstractmethod
    async def find_trip_admins(self, trip_id: str) -> List[TripMember]:
        pass

    @abstractmethod
    async def find_by_user_id(
        self, 
        user_id: str, 
        page: int = 1, 
        limit: int = 20
    ) -> tuple[List[TripMember], int]:
        pass

    @abstractmethod
    async def find_active_by_user_id(self, user_id: str) -> List[TripMember]:
        pass

    @abstractmethod
    async def find_pending_invitations_by_user_id(self, user_id: str) -> List[TripMember]:
        pass

    @abstractmethod
    async def find_user_trips_with_role(self, user_id: str, role: str) -> List[TripMember]:
        pass

    @abstractmethod
    async def find_by_trip_and_user(
        self, 
        trip_id: str, 
        user_id: str
    ) -> Optional[TripMember]:
        pass

    @abstractmethod
    async def find_by_trip_and_role(self, trip_id: str, role: str) -> List[TripMember]:
        pass

    @abstractmethod
    async def find_by_trip_and_status(self, trip_id: str, status: str) -> List[TripMember]:
        pass

    @abstractmethod
    async def exists_by_trip_and_user(self, trip_id: str, user_id: str) -> bool:
        pass

    @abstractmethod
    async def is_user_member_of_trip(self, trip_id: str, user_id: str) -> bool:
        pass

    @abstractmethod
    async def is_user_owner_of_trip(self, trip_id: str, user_id: str) -> bool:
        pass

    @abstractmethod
    async def is_user_admin_of_trip(self, trip_id: str, user_id: str) -> bool:
        pass

    @abstractmethod
    async def can_user_access_trip(self, trip_id: str, user_id: str) -> bool:
        pass

    @abstractmethod
    async def count_members_by_trip_id(self, trip_id: str) -> int:
        pass

    @abstractmethod
    async def count_active_members_by_trip_id(self, trip_id: str) -> int:
        pass

    @abstractmethod
    async def count_pending_members_by_trip_id(self, trip_id: str) -> int:
        pass

    @abstractmethod
    async def count_trips_by_user_id(self, user_id: str) -> int:
        pass

    @abstractmethod
    async def search(self, query: str, trip_id: Optional[str] = None) -> List[TripMember]:
        pass

    @abstractmethod
    async def find_with_filters(
        self, 
        filters: Dict[str, Any], 
        page: int = 1, 
        limit: int = 20
    ) -> tuple[List[TripMember], int]:
        pass

    @abstractmethod
    async def count_by_filters(self, filters: Dict[str, Any]) -> int:
        pass

    @abstractmethod
    async def delete_by_trip_id(self, trip_id: str) -> bool:
        pass

    @abstractmethod
    async def delete_by_user_id(self, user_id: str) -> bool:
        pass

    @abstractmethod
    async def cleanup_rejected_invitations(self, older_than_days: int) -> int:
        pass