from typing import Dict, Any
from ...domain.expense_service import ExpenseService
from ...domain.interfaces.expense_repository_interface import ExpenseRepositoryInterface
from ...domain.expense_events import ExpenseDeletedEvent
from shared.errors.custom_errors import NotFoundError, AuthorizationError
from shared.events.event_bus import EventBus


class DeleteExpense:
    def __init__(
        self, 
        expense_repository: ExpenseRepositoryInterface,
        expense_service: ExpenseService,
        event_bus: EventBus
    ):
        self._expense_repository = expense_repository
        self._expense_service = expense_service
        self._event_bus = event_bus

    async def execute(self, expense_id: str, user_id: str) -> Dict[str, Any]:
        """Eliminar gasto (soft delete)"""
        
        # Buscar gasto
        expense = await self._expense_repository.find_by_id(expense_id)
        if not expense:
            raise NotFoundError("Gasto no encontrado")

        # Validar permisos
        await self._expense_service.validate_expense_permissions(expense, user_id)

        # Validar que no esté ya eliminado
        if not expense.is_active():
            raise ValidationError("El gasto ya está eliminado")

        # Guardar datos para el evento antes de eliminar
        expense_data = {
            "expense_id": expense.id,
            "trip_id": expense.trip_id,
            "amount": expense.amount,
            "currency": expense.currency
        }

        # Realizar eliminación suave
        expense.soft_delete()
        await self._expense_repository.update(expense)

        # Publicar evento
        event = ExpenseDeletedEvent(
            expense_id=expense_data["expense_id"],
            trip_id=expense_data["trip_id"],
            user_id=user_id,
            amount=expense_data["amount"],
            currency=expense_data["currency"]
        )
        await self._event_bus.publish(event)

        return {
            "success": True,
            "message": "Gasto eliminado exitosamente",
            "data": {
                "expense_id": expense.id,
                "deleted_at": expense._data.updated_at.isoformat()
            }
        }