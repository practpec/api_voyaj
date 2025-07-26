from ..dtos.expense_dto import ExpenseResponseDTO, ExpenseDTOMapper
from ...domain.expense_service import ExpenseService
from ...domain.interfaces.expense_repository_interface import ExpenseRepositoryInterface
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from shared.errors.custom_errors import NotFoundError, ForbiddenError


class GetExpenseUseCase:
    def __init__(
        self,
        expense_repository: ExpenseRepositoryInterface,
        expense_service: ExpenseService,
        user_repository: IUserRepository
    ):
        self._expense_repository = expense_repository
        self._expense_service = expense_service
        self._user_repository = user_repository

    async def execute(self, expense_id: str, user_id: str) -> ExpenseResponseDTO:
        """Obtener gasto específico por ID"""
        
        expense = await self._expense_repository.find_by_id(expense_id)
        if not expense or not expense.is_active():
            raise NotFoundError("Gasto no encontrado")

        # Verificar acceso del usuario
        can_access = await self._expense_service.can_user_access_expense(expense, user_id)
        if not can_access:
            raise ForbiddenError("No tienes acceso a este gasto")

        # Determinar permisos del usuario
        can_edit = expense.user_id == user_id
        can_delete = expense.user_id == user_id
        can_change_status = can_edit

        return ExpenseDTOMapper.to_expense_response(
            expense.to_public_data(),
            can_edit=can_edit,
            can_delete=can_delete,
            can_change_status=can_change_status
        )