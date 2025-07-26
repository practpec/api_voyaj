from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import datetime, timedelta
from .expense import Expense, ExpenseCategory, ExpenseStatus
from .interfaces.expense_repository_interface import ExpenseRepositoryInterface
from shared.errors.custom_errors import ValidationError, NotFoundError, AuthorizationError


class ExpenseService:
    def __init__(self, expense_repository: ExpenseRepositoryInterface):
        self._expense_repository = expense_repository

    async def calculate_trip_total(self, trip_id: str, currency: Optional[str] = None) -> Dict[str, Any]:
        """Calcular total de gastos del viaje por moneda"""
        expenses = await self._expense_repository.find_by_trip_id(trip_id)
        active_expenses = [e for e in expenses if e.is_active()]

        if not active_expenses:
            return {"total_by_currency": {}, "overall_total": Decimal("0")}

        totals_by_currency = {}
        for expense in active_expenses:
            curr = expense.currency
            if curr not in totals_by_currency:
                totals_by_currency[curr] = Decimal("0")
            totals_by_currency[curr] += expense.amount

        # Si se especifica una moneda, filtrar solo esa
        if currency:
            return {
                "total_by_currency": {currency: totals_by_currency.get(currency, Decimal("0"))},
                "overall_total": totals_by_currency.get(currency, Decimal("0"))
            }

        # Calcular total general (asumiendo primera moneda como base)
        main_currency = list(totals_by_currency.keys())[0] if totals_by_currency else "USD"
        overall_total = totals_by_currency.get(main_currency, Decimal("0"))

        return {
            "total_by_currency": totals_by_currency,
            "overall_total": overall_total,
            "main_currency": main_currency
        }

    async def get_expenses_by_category(self, trip_id: str) -> Dict[ExpenseCategory, Decimal]:
        """Obtener gastos agrupados por categoría"""
        expenses = await self._expense_repository.find_by_trip_id(trip_id)
        active_expenses = [e for e in expenses if e.is_active()]

        category_totals = {}
        for expense in active_expenses:
            category = expense.category
            if category not in category_totals:
                category_totals[category] = Decimal("0")
            category_totals[category] += expense.amount

        return category_totals

    async def get_daily_expenses(self, trip_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Obtener gastos de los últimos N días"""
        start_date = datetime.utcnow() - timedelta(days=days)
        expenses = await self._expense_repository.find_by_trip_id_and_date_range(
            trip_id, start_date, datetime.utcnow()
        )

        daily_expenses = {}
        for expense in expenses:
            if not expense.is_active():
                continue

            date_key = expense._data.expense_date.date()
            if date_key not in daily_expenses:
                daily_expenses[date_key] = {
                    "date": date_key,
                    "total": Decimal("0"),
                    "count": 0,
                    "expenses": []
                }

            daily_expenses[date_key]["total"] += expense.amount
            daily_expenses[date_key]["count"] += 1
            daily_expenses[date_key]["expenses"].append({
                "id": expense.id,
                "amount": expense.amount,
                "currency": expense.currency,
                "category": expense.category.value,
                "description": expense._data.description
            })

        return list(daily_expenses.values())

    async def get_user_expenses_in_trip(self, trip_id: str, user_id: str) -> List[Expense]:
        """Obtener gastos de un usuario específico en un viaje"""
        expenses = await self._expense_repository.find_by_trip_and_user_id(trip_id, user_id)
        return [e for e in expenses if e.is_active()]

    async def get_shared_expenses(self, trip_id: str) -> List[Expense]:
        """Obtener gastos compartidos del viaje"""
        expenses = await self._expense_repository.find_shared_by_trip_id(trip_id)
        return [e for e in expenses if e.is_active()]

    async def validate_expense_permissions(self, expense: Expense, user_id: str) -> bool:
        """Validar permisos del usuario sobre el gasto"""
        if not expense.can_be_edited_by(user_id):
            raise AuthorizationError("No tienes permisos para editar este gasto")
        return True

    async def calculate_average_daily_spending(self, trip_id: str, days: int = 30) -> Dict[str, Any]:
        """Calcular promedio de gasto diario"""
        start_date = datetime.utcnow() - timedelta(days=days)
        expenses = await self._expense_repository.find_by_trip_id_and_date_range(
            trip_id, start_date, datetime.utcnow()
        )

        active_expenses = [e for e in expenses if e.is_active()]
        
        if not active_expenses:
            return {"average_daily": Decimal("0"), "total_days": 0, "total_amount": Decimal("0")}

        total_amount = sum(expense.amount for expense in active_expenses)
        unique_days = len(set(expense._data.expense_date.date() for expense in active_expenses))

        average_daily = total_amount / unique_days if unique_days > 0 else Decimal("0")

        return {
            "average_daily": average_daily,
            "total_days": unique_days,
            "total_amount": total_amount,
            "expense_count": len(active_expenses)
        }

    async def find_expenses_by_category_and_date(
        self, 
        trip_id: str, 
        category: ExpenseCategory, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Expense]:
        """Buscar gastos por categoría y rango de fechas"""
        expenses = await self._expense_repository.find_by_category_and_date_range(
            trip_id, category, start_date, end_date
        )
        return [e for e in expenses if e.is_active()]

    async def get_top_expenses(self, trip_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtener los gastos más altos del viaje"""
        expenses = await self._expense_repository.find_by_trip_id(trip_id)
        active_expenses = [e for e in expenses if e.is_active()]

        # Ordenar por monto descendente
        sorted_expenses = sorted(active_expenses, key=lambda x: x.amount, reverse=True)

        return [
            {
                "id": expense.id,
                "amount": expense.amount,
                "currency": expense.currency,
                "category": expense.category.value,
                "description": expense._data.description,
                "date": expense._data.expense_date,
                "location": expense._data.location
            }
            for expense in sorted_expenses[:limit]
        ]

    async def validate_expense_amount_limits(self, amount: Decimal, currency: str) -> bool:
        """Validar límites de monto por moneda"""
        # Límites básicos por moneda
        limits = {
            "USD": Decimal("10000"),
            "EUR": Decimal("10000"),
            "MXN": Decimal("200000"),
            "CAD": Decimal("15000"),
            "GBP": Decimal("8000")
        }

        max_amount = limits.get(currency, Decimal("10000"))
        
        if amount > max_amount:
            raise ValidationError(f"El monto excede el límite máximo de {max_amount} {currency}")

        return True

    async def get_receipt_required_categories(self) -> List[ExpenseCategory]:
        """Obtener categorías que requieren comprobante"""
        return [
            ExpenseCategory.ACCOMMODATION,
            ExpenseCategory.TRANSPORTATION,
            ExpenseCategory.HEALTHCARE,
            ExpenseCategory.INSURANCE
        ]

    async def should_require_receipt(self, expense: Expense) -> bool:
        """Determinar si el gasto requiere comprobante"""
        required_categories = await self.get_receipt_required_categories()
        
        # Requerir comprobante si es categoría específica o monto alto
        return (
            expense.category in required_categories or 
            expense.amount > Decimal("100")  # Más de 100 en cualquier moneda
        )

    async def generate_expense_timeline(self, trip_id: str) -> List[Dict[str, Any]]:
        """Generar timeline de gastos del viaje"""
        expenses = await self._expense_repository.find_by_trip_id(trip_id)
        active_expenses = [e for e in expenses if e.is_active()]

        timeline = []
        for expense in sorted(active_expenses, key=lambda x: x._data.expense_date):
            timeline.append({
                "id": expense.id,
                "date": expense._data.expense_date,
                "amount": expense.amount,
                "currency": expense.currency,
                "category": expense.category.value,
                "description": expense._data.description,
                "location": expense._data.location,
                "is_shared": expense.is_shared,
                "status": expense.status.value
            })

        return timeline