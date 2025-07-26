from ..dtos.expense_dto import ChangeExpenseStatusDTO, ExpenseResponseDTO, ExpenseDTOMapper
from ...domain.expense_service import ExpenseService
from ...domain.interfaces.expense_repository_interface import ExpenseRepositoryInterface
from shared.errors.custom_errors import NotFoundError


class ChangeExpenseStatusUseCase:
    def __init__(
        self,
        expense_repository: ExpenseRepositoryInterface,
        expense_service: ExpenseService
    ):
        self._expense_repository = expense_repository
        self._expense_service = expense_service

    async def execute(
        self, expense_id: str, dto: ChangeExpenseStatusDTO, user_id: str
    ) -> ExpenseResponseDTO:
        """Cambiar estado del gasto"""
        
        expense = await self._expense_repository.find_by_id(expense_id)
        if not expense or not expense.is_active():
            raise NotFoundError("Gasto no encontrado")

        # Validar permisos
        await self._expense_service.validate_expense_status_change(expense, user_id)

        # Cambiar estado
        expense.change_status(dto.status.value)
        if dto.notes:
            expense.add_status_note(dto.notes)

        # Guardar cambios
        updated_expense = await self._expense_repository.save(expense)

        # Determinar permisos
        can_edit = updated_expense.user_id == user_id
        can_delete = updated_expense.user_id == user_id
        can_change_status = can_edit

        return ExpenseDTOMapper.to_expense_response(
            updated_expense.to_public_data(),
            can_edit=can_edit,
            can_delete=can_delete,
            can_change_status=can_change_status
        )