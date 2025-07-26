from typing import Dict, Any
from ..dtos.expense_split_dto import ExpenseSplitsResponseDTO, ExpenseSplitResponseDTO
from ...domain.interfaces.expense_split_repository_interface import ExpenseSplitRepositoryInterface
from shared.errors.custom_errors import NotFoundError


class GetExpenseSplitsUseCase:
    def __init__(
        self,
        expense_split_repository: ExpenseSplitRepositoryInterface
    ):
        self._expense_split_repository = expense_split_repository

    async def execute(self, expense_id: str, user_id: str) -> ExpenseSplitsResponseDTO:
        """Obtener divisiones de un gasto"""
        expense_splits = await self._expense_split_repository.find_by_expense_id(expense_id)
        
        if not expense_splits:
            return ExpenseSplitsResponseDTO(
                expense_id=expense_id,
                total_amount=0,
                splits=[],
                pending_count=0,
                paid_count=0
            )

        # Convertir a DTOs
        split_dtos = []
        total_amount = 0
        pending_count = 0
        paid_count = 0

        for split in expense_splits:
            if split.is_active():
                split_dto = ExpenseSplitResponseDTO(
                    id=split.id,
                    expense_id=split.expense_id,
                    user_id=split.user_id,
                    amount=split.amount,
                    status=split.status.value,
                    paid_at=split.paid_at,
                    notes=split.notes,
                    created_at=split.created_at,
                    updated_at=split.updated_at
                )
                split_dtos.append(split_dto)
                total_amount += split.amount
                
                if split.is_paid():
                    paid_count += 1
                else:
                    pending_count += 1

        return ExpenseSplitsResponseDTO(
            expense_id=expense_id,
            total_amount=total_amount,
            splits=split_dtos,
            pending_count=pending_count,
            paid_count=paid_count
        )