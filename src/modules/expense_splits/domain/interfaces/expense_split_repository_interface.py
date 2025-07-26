from abc import ABC, abstractmethod
from typing import List, Optional
from ..expense_split import ExpenseSplit


class ExpenseSplitRepositoryInterface(ABC):
    
    @abstractmethod
    async def create(self, expense_split: ExpenseSplit) -> ExpenseSplit:
        """Crear nueva división de gasto"""
        pass
    
    @abstractmethod
    async def find_by_id(self, expense_split_id: str) -> Optional[ExpenseSplit]:
        """Buscar división por ID"""
        pass
    
    @abstractmethod
    async def find_by_expense_id(self, expense_id: str) -> List[ExpenseSplit]:
        """Buscar divisiones por ID de gasto"""
        pass
    
    @abstractmethod
    async def find_by_user_id(self, user_id: str) -> List[ExpenseSplit]:
        """Buscar divisiones por ID de usuario"""
        pass
    
    @abstractmethod
    async def find_by_expense_and_user(self, expense_id: str, user_id: str) -> Optional[ExpenseSplit]:
        """Buscar división específica por gasto y usuario"""
        pass
    
    @abstractmethod
    async def update(self, expense_split: ExpenseSplit) -> ExpenseSplit:
        """Actualizar división de gasto"""
        pass
    
    @abstractmethod
    async def delete(self, expense_split_id: str) -> bool:
        """Eliminar división de gasto"""
        pass
    
    @abstractmethod
    async def delete_by_expense_id(self, expense_id: str) -> bool:
        """Eliminar todas las divisiones de un gasto"""
        pass
    
    @abstractmethod
    async def get_user_pending_splits(self, user_id: str) -> List[ExpenseSplit]:
        """Obtener divisiones pendientes de un usuario"""
        pass
    
    @abstractmethod
    async def get_trip_balances(self, trip_id: str) -> List[dict]:
        """Obtener balances de usuarios en un viaje"""
        pass