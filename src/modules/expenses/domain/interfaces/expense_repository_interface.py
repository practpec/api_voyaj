from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from ..expense import Expense, ExpenseCategory


class ExpenseRepositoryInterface(ABC):
    """Interface para repositorio de gastos"""

    @abstractmethod
    async def save(self, expense: Expense) -> None:
        """Guardar gasto"""
        pass

    @abstractmethod
    async def find_by_id(self, expense_id: str) -> Optional[Expense]:
        """Buscar gasto por ID"""
        pass

    @abstractmethod
    async def find_by_trip_id(self, trip_id: str) -> List[Expense]:
        """Buscar gastos por ID de viaje"""
        pass

    @abstractmethod
    async def find_by_trip_and_user_id(self, trip_id: str, user_id: str) -> List[Expense]:
        """Buscar gastos por viaje y usuario"""
        pass

    @abstractmethod
    async def find_shared_by_trip_id(self, trip_id: str) -> List[Expense]:
        """Buscar gastos compartidos por viaje"""
        pass

    @abstractmethod
    async def find_by_activity_id(self, activity_id: str) -> List[Expense]:
        """Buscar gastos por actividad"""
        pass

    @abstractmethod
    async def find_by_diary_entry_id(self, diary_entry_id: str) -> List[Expense]:
        """Buscar gastos por entrada de diario"""
        pass

    @abstractmethod
    async def find_by_trip_id_and_date_range(
        self, 
        trip_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Expense]:
        """Buscar gastos por viaje y rango de fechas"""
        pass

    @abstractmethod
    async def find_by_category_and_date_range(
        self, 
        trip_id: str, 
        category: ExpenseCategory, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Expense]:
        """Buscar gastos por categoría y rango de fechas"""
        pass

    @abstractmethod
    async def find_by_paid_by_user_id(self, trip_id: str, user_id: str) -> List[Expense]:
        """Buscar gastos pagados por usuario específico"""
        pass

    @abstractmethod
    async def update(self, expense: Expense) -> None:
        """Actualizar gasto"""
        pass

    @abstractmethod
    async def delete(self, expense_id: str) -> None:
        """Eliminar gasto (soft delete)"""
        pass

    @abstractmethod
    async def exists_by_id(self, expense_id: str) -> bool:
        """Verificar si existe gasto por ID"""
        pass

    @abstractmethod
    async def count_by_trip_id(self, trip_id: str) -> int:
        """Contar gastos activos por viaje"""
        pass

    @abstractmethod
    async def find_with_receipt_by_trip_id(self, trip_id: str) -> List[Expense]:
        """Buscar gastos que tienen comprobante"""
        pass

    @abstractmethod
    async def find_without_receipt_by_trip_id(self, trip_id: str) -> List[Expense]:
        """Buscar gastos sin comprobante"""
        pass