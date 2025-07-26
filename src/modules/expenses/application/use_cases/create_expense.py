from ..dtos.expense_dto import CreateExpenseDTO, ExpenseResponseDTO, ExpenseDTOMapper
from ...domain.expense import Expense
from ...domain.expense_service import ExpenseService
from ...domain.interfaces.expense_repository_interface import ExpenseRepositoryInterface


class CreateExpenseUseCase:
    def __init__(
        self,
        expense_repository: ExpenseRepositoryInterface,
        expense_service: ExpenseService
    ):
        self._expense_repository = expense_repository
        self._expense_service = expense_service

    async def execute(self, dto: CreateExpenseDTO, user_id: str) -> ExpenseResponseDTO:
        """Crear nuevo gasto"""
        
        # Validar creación del gasto
        trip_id = await self._expense_service.validate_expense_creation(
            trip_id=dto.trip_id,
            user_id=user_id,
            amount=dto.amount,
            currency=dto.currency
        )

        # Crear entidad de gasto
        expense = Expense.create(
            trip_id=dto.trip_id,
            user_id=user_id,
            amount=dto.amount,
            currency=dto.currency,
            category=dto.category.value,
            description=dto.description,
            expense_date=dto.expense_date,
            is_shared=dto.is_shared,
            paid_by_user_id=dto.paid_by_user_id or user_id,
            activity_id=dto.activity_id,
            diary_entry_id=dto.diary_entry_id,
            location=dto.location,
            receipt_url=dto.receipt_url,
            metadata=dto.metadata
        )

        # Guardar en repositorio
        created_expense = await self._expense_repository.save(expense)

        # Determinar permisos del usuario
        can_edit = created_expense.user_id == user_id
        can_delete = created_expense.user_id == user_id
        can_change_status = can_edit

        # Retornar DTO de respuesta
        return ExpenseDTOMapper.to_expense_response(
            created_expense.to_public_data(),
            can_edit=can_edit,
            can_delete=can_delete,
            can_change_status=can_change_status
        )