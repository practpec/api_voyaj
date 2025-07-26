from ...domain.expense_service import ExpenseService
from ...domain.interfaces.expense_repository_interface import ExpenseRepositoryInterface
from shared.errors.custom_errors import NotFoundError


class DeleteExpenseUseCase:
    def __init__(
        self,
        expense_repository: ExpenseRepositoryInterface,
        expense_service: ExpenseService
    ):
        self._expense_repository = expense_repository
        self._expense_service = expense_service

    async def execute(self, expense_id: str, user_id: str) -> None:
        """Eliminar gasto"""
        
        expense = await self._expense_repository.find_by_id(expense_id)
        if not expense or not expense.is_active():
            raise NotFoundError("Gasto no encontrado")

        # Validar permisos
        await self._expense_service.validate_expense_deletion(expense, user_id)

        # Eliminar (soft delete)
        expense.soft_delete()
        await self._expense_repository.save(expense)