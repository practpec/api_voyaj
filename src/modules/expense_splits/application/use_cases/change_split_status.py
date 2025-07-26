from ..dtos.expense_split_dto import ChangeExpenseSplitStatusDTO, ExpenseSplitResponseDTO
from ...domain.interfaces.expense_split_repository_interface import ExpenseSplitRepositoryInterface
from ...domain.expense_split_service import ExpenseSplitService
from shared.errors.custom_errors import NotFoundError, ForbiddenError, ValidationError


class ChangeSplitStatusUseCase:
    def __init__(
        self,
        expense_split_repository: ExpenseSplitRepositoryInterface,
        expense_split_service: ExpenseSplitService
    ):
        self._expense_split_repository = expense_split_repository
        self._expense_split_service = expense_split_service

    async def execute(
        self, 
        expense_split_id: str, 
        dto: ChangeExpenseSplitStatusDTO, 
        user_id: str
    ) -> ExpenseSplitResponseDTO:
        """Cambiar estado de una división"""
        
        # Buscar división
        expense_split = await self._expense_split_repository.find_by_id(expense_split_id)
        if not expense_split:
            raise NotFoundError("División de gasto no encontrada")

        # Validar acceso
        if not await self._expense_split_service.validate_split_access(expense_split, user_id):
            raise ForbiddenError("No tienes permisos para modificar esta división")

        # Cambiar estado según el tipo
        if dto.status == "paid":
            updated_split = await self._expense_split_service.mark_split_as_paid(
                expense_split_id, dto.notes
            )
        elif dto.status == "pending":
            updated_split = await self._expense_split_service.mark_split_as_pending(expense_split_id)
        elif dto.status == "cancelled":
            updated_split = await self._expense_split_service.cancel_split(expense_split_id)
        else:
            raise ValidationError("Estado no válido. Use: pending, paid, cancelled")

        return ExpenseSplitResponseDTO(
            id=updated_split.id,
            expense_id=updated_split.expense_id,
            user_id=updated_split.user_id,
            amount=updated_split.amount,
            status=updated_split.status.value,
            paid_at=updated_split.paid_at,
            notes=updated_split.notes,
            created_at=updated_split.created_at,
            updated_at=updated_split.updated_at
        )