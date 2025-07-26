from ..dtos.expense_dto import UpdateExpenseDTO, ExpenseResponseDTO, ExpenseDTOMapper
from ...domain.expense_service import ExpenseService
from ...domain.interfaces.expense_repository_interface import ExpenseRepositoryInterface
from shared.errors.custom_errors import NotFoundError


class UpdateExpenseUseCase:
    def __init__(
        self,
        expense_repository: ExpenseRepositoryInterface,
        expense_service: ExpenseService
    ):
        self._expense_repository = expense_repository
        self._expense_service = expense_service

    async def execute(
        self, expense_id: str, dto: UpdateExpenseDTO, user_id: str
    ) -> ExpenseResponseDTO:
        """Actualizar gasto existente"""
        
        # Buscar el gasto
        expense = await self._expense_repository.find_by_id(expense_id)
        if not expense or not expense.is_active():
            raise NotFoundError("Gasto no encontrado")

        # Validar permisos de actualización
        trip_id = await self._expense_service.validate_expense_update(expense, user_id)

        # Actualizar campos si se proporcionan
        if dto.amount is not None:
            expense.update_amount(dto.amount)

        if dto.currency is not None:
            expense.update_currency(dto.currency)

        if dto.category is not None:
            expense.update_category(dto.category.value)

        if dto.description is not None:
            expense.update_description(dto.description)

        if dto.expense_date is not None:
            expense.update_expense_date(dto.expense_date)

        if dto.is_shared is not None:
            if dto.is_shared:
                expense.make_shared()
            else:
                expense.make_individual()

        if dto.paid_by_user_id is not None:
            expense.change_payer(dto.paid_by_user_id)

        if dto.activity_id is not None:
            expense.associate_with_activity(dto.activity_id)

        if dto.diary_entry_id is not None:
            expense.associate_with_diary_entry(dto.diary_entry_id)

        if dto.location is not None:
            expense.set_location(dto.location)

        if dto.receipt_url is not None:
            expense.set_receipt_url(dto.receipt_url)

        if dto.metadata is not None:
            expense.update_metadata(dto.metadata)

        # Guardar cambios
        updated_expense = await self._expense_repository.save(expense)

        # Determinar permisos del usuario
        can_edit = updated_expense.user_id == user_id
        can_delete = updated_expense.user_id == user_id
        can_change_status = can_edit

        # Retornar DTO de respuesta
        return ExpenseDTOMapper.to_expense_response(
            updated_expense.to_public_data(),
            can_edit=can_edit,
            can_delete=can_delete,
            can_change_status=can_change_status
        )