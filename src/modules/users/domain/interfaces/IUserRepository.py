from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from ..User import User

class IUserRepository(ABC):
    
    @abstractmethod
    async def create(self, user: User) -> None:
        pass
    
    @abstractmethod
    async def find_by_id(self, user_id: str) -> Optional[User]:
        pass
    
    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]:
        pass
    
    @abstractmethod
    async def update(self, user: User) -> None:
        pass
    
    @abstractmethod
    async def delete(self, user_id: str) -> None:
        pass
    
    @abstractmethod
    async def search_users(self, query: str, limit: int = 10, offset: int = 0) -> List[User]:
        pass
    
    @abstractmethod
    async def count_users(self, filters: Optional[Dict[str, Any]] = None) -> int:
        pass
    
    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        pass