from typing import Dict, Any, Optional
from ...domain.interfaces.expense_repository_interface import ExpenseRepositoryInterface
from shared.errors.custom_errors import NotFoundError


class GetExpense:
    def __init__(self, expense_repository: ExpenseRepositoryInterface):
        self._expense_repository = expense_repository

    async def execute(self, expense_id: str, user_id: str) -> Dict[str, Any]:
        """Obtener detalles de un gasto específico"""
        
        # Buscar gasto
        expense = await self._expense_repository.find_by_id(expense_id)
        if not expense:
            raise NotFoundError("Gasto no encontrado")

        # Verificar que esté activo
        if not expense.is_active():
            raise NotFoundError("Gasto no encontrado")

        # Convertir a formato de respuesta
        return {
            "success": True,
            "data": {
                "id": expense.id,
                "trip_id": expense.trip_id,
                "user_id": expense._data.user_id,
                "activity_id": expense._data.activity_id,
                "diary_entry_id": expense._data.diary_entry_id,
                "amount": float(expense.amount),
                "currency": expense.currency,
                "category": {
                    "value": expense.category.value,
                    "display": expense.get_category_display()
                },
                "description": expense._data.description,
                "receipt_url": expense._data.receipt_url,
                "location": expense._data.location,
                "expense_date": expense._data.expense_date.isoformat(),
                "is_shared": expense.is_shared,
                "paid_by_user_id": expense._data.paid_by_user_id,
                "status": expense.status.value,
                "metadata": expense._data.metadata,
                "created_at": expense._data.created_at.isoformat(),
                "updated_at": expense._data.updated_at.isoformat(),
                "can_edit": expense.can_be_edited_by(user_id),
                "can_split": expense.can_be_split()
            }
        }