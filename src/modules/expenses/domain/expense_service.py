from typing import Dict, Any
from decimal import Decimal
from .expense import Expense
from .interfaces.expense_repository_interface import ExpenseRepositoryInterface
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from modules.trips.domain.interfaces.trip_repository import ITripRepository
from shared.errors.custom_errors import ValidationError, NotFoundError, ForbiddenError


class ExpenseService:
    def __init__(
        self,
        expense_repository: ExpenseRepositoryInterface,
        trip_member_repository: ITripMemberRepository,
        user_repository: IUserRepository,
        trip_repository: ITripRepository
    ):
        self._expense_repository = expense_repository
        self._trip_member_repository = trip_member_repository
        self._user_repository = user_repository
        self._trip_repository = trip_repository

    async def validate_expense_creation(
        self,
        trip_id: str,
        user_id: str,
        amount: Decimal,
        currency: str
    ) -> str:
        """Validar creación de gasto y retornar trip_id"""
        # Verificar que el viaje existe
        trip = await self._trip_repository.find_by_id(trip_id)
        if not trip or not trip.is_active():
            raise NotFoundError("Viaje no encontrado")

        # Verificar que el usuario es miembro del viaje
        trip_member = await self._trip_member_repository.find_by_trip_and_user(trip_id, user_id)
        if not trip_member or not trip_member.is_active():
            raise ForbiddenError("No eres miembro de este viaje")

        # Validar monto
        if amount <= 0:
            raise ValidationError("El monto debe ser mayor a cero")
        
        if amount > Decimal('999999.99'):
            raise ValidationError("El monto no puede ser mayor a 999,999.99")

        # Validar moneda
        if not currency or len(currency) != 3:
            raise ValidationError("La moneda debe ser un código ISO de 3 letras")

        return trip_id

    async def validate_expense_update(self, expense: Expense, user_id: str) -> str:
        """Validar actualización de gasto y retornar trip_id"""
        if not expense.is_active():
            raise ValidationError("No se puede actualizar un gasto eliminado")

        # Solo el creador puede actualizar
        if expense.user_id != user_id:
            raise ForbiddenError("Solo puedes actualizar tus propios gastos")

        # Obtener trip_id del gasto
        trip = await self._trip_repository.find_by_id(expense.trip_id)
        if not trip:
            raise NotFoundError("Viaje no encontrado")

        return expense.trip_id

    async def validate_expense_deletion(self, expense: Expense, user_id: str) -> None:
        """Validar eliminación de gasto"""
        if not expense.is_active():
            raise ValidationError("El gasto ya está eliminado")

        # Solo el creador puede eliminar
        if expense.user_id != user_id:
            raise ForbiddenError("Solo puedes eliminar tus propios gastos")

    async def validate_expense_status_change(self, expense: Expense, user_id: str) -> None:
        """Validar cambio de estado de gasto"""
        if not expense.is_active():
            raise ValidationError("No se puede cambiar el estado de un gasto eliminado")

        # Solo el creador puede cambiar estado
        if expense.user_id != user_id:
            raise ForbiddenError("Solo puedes cambiar el estado de tus propios gastos")

    async def can_user_access_expense(self, expense: Expense, user_id: str) -> bool:
        """Verificar si el usuario puede acceder al gasto"""
        # Verificar si es miembro del viaje
        trip_member = await self._trip_member_repository.find_by_trip_and_user(expense.trip_id, user_id)
        return trip_member is not None and trip_member.is_active()

    async def get_trip_expense_summary(self, trip_id: str) -> Dict[str, Any]:
        """Obtener resumen básico de gastos del viaje"""
        expenses = await self._expense_repository.find_by_trip_id(trip_id)
        active_expenses = [e for e in expenses if e.is_active()]

        total_amount = sum(e.amount for e in active_expenses)
        shared_count = len([e for e in active_expenses if e.is_shared])
        individual_count = len(active_expenses) - shared_count

        # Contar por categoría
        by_category = {}
        for expense in active_expenses:
            category = expense.category.value
            by_category[category] = by_category.get(category, 0) + 1

        return {
            "total_amount": total_amount,
            "currency": active_expenses[0].currency if active_expenses else "USD",
            "shared_count": shared_count,
            "individual_count": individual_count,
            "by_category": by_category
        }

    async def get_detailed_expense_summary(self, trip_id: str) -> Dict[str, Any]:
        """Obtener resumen detallado de gastos del viaje"""
        expenses = await self._expense_repository.find_by_trip_id(trip_id)
        active_expenses = [e for e in expenses if e.is_active()]

        if not active_expenses:
            return {
                "total_amount": Decimal('0'),
                "currency": "USD",
                "total_expenses": 0,
                "by_category": {},
                "by_user": {},
                "shared_amount": Decimal('0'),
                "individual_amount": Decimal('0'),
                "average_per_expense": Decimal('0')
            }

        total_amount = sum(e.amount for e in active_expenses)
        shared_amount = sum(e.amount for e in active_expenses if e.is_shared)
        individual_amount = total_amount - shared_amount

        # Por categoría
        by_category = {}
        for expense in active_expenses:
            category = expense.category.value
            by_category[category] = by_category.get(category, Decimal('0')) + expense.amount

        # Por usuario
        by_user = {}
        for expense in active_expenses:
            user_id = expense.user_id
            by_user[user_id] = by_user.get(user_id, Decimal('0')) + expense.amount

        # Promedio
        average_per_expense = total_amount / len(active_expenses) if active_expenses else Decimal('0')

        return {
            "total_amount": total_amount,
            "currency": active_expenses[0].currency,
            "total_expenses": len(active_expenses),
            "by_category": by_category,
            "by_user": by_user,
            "shared_amount": shared_amount,
            "individual_amount": individual_amount,
            "average_per_expense": average_per_expense
        }