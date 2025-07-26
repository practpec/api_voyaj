from typing import Dict, Any, List, Optional
from ...domain.expense_service import ExpenseService
from ...domain.interfaces.expense_repository_interface import ExpenseRepositoryInterface


class GetTripExpenses:
    def __init__(
        self, 
        expense_repository: ExpenseRepositoryInterface,
        expense_service: ExpenseService
    ):
        self._expense_repository = expense_repository
        self._expense_service = expense_service

    async def execute(
        self, 
        trip_id: str, 
        user_id: str,
        include_summary: bool = True,
        category_filter: Optional[str] = None,
        user_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """Obtener gastos de un viaje con filtros opcionales"""
        
        # Obtener gastos base
        expenses = await self._expense_repository.find_by_trip_id(trip_id)
        active_expenses = [e for e in expenses if e.is_active()]

        # Aplicar filtros
        if category_filter:
            active_expenses = [e for e in active_expenses if e.category.value == category_filter]

        if user_filter:
            active_expenses = [e for e in active_expenses if e._data.user_id == user_filter]

        # Convertir a formato de respuesta
        expenses_data = []
        for expense in active_expenses:
            expenses_data.append({
                "id": expense.id,
                "amount": float(expense.amount),
                "currency": expense.currency,
                "category": {
                    "value": expense.category.value,
                    "display": expense.get_category_display()
                },
                "description": expense._data.description,
                "location": expense._data.location,
                "expense_date": expense._data.expense_date.isoformat(),
                "is_shared": expense.is_shared,
                "paid_by_user_id": expense._data.paid_by_user_id,
                "status": expense.status.value,
                "has_receipt": bool(expense._data.receipt_url),
                "activity_id": expense._data.activity_id,
                "diary_entry_id": expense._data.diary_entry_id,
                "created_at": expense._data.created_at.isoformat(),
                "can_edit": expense.can_be_edited_by(user_id)
            })

        response = {
            "success": True,
            "data": {
                "expenses": expenses_data,
                "total_count": len(expenses_data),
                "filters_applied": {
                    "category": category_filter,
                    "user": user_filter
                }
            }
        }

        # Incluir resumen si se solicita
        if include_summary:
            summary = await self._expense_service.calculate_trip_total(trip_id)
            categories = await self._expense_service.get_expenses_by_category(trip_id)
            
            response["data"]["summary"] = {
                "total_by_currency": {k: float(v) for k, v in summary["total_by_currency"].items()},
                "overall_total": float(summary["overall_total"]),
                "main_currency": summary.get("main_currency", "USD"),
                "categories": {k.value: float(v) for k, v in categories.items()},
                "shared_expenses_count": len([e for e in active_expenses if e.is_shared]),
                "expenses_with_receipt": len([e for e in active_expenses if e._data.receipt_url])
            }

        return response