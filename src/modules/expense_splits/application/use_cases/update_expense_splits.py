from typing import List
from ..dtos.expense_split_dto import UpdateExpenseSplitsDTO, ExpenseSplitsResponseDTO, ExpenseSplitResponseDTO
from ...domain.interfaces.expense_split_repository_interface import ExpenseSplitRepositoryInterface
from ...domain.expense_split_service import ExpenseSplitService
from shared.errors.custom_errors import ValidationError


class UpdateExpenseSplitsUseCase:
    def __init__(
        self,
        expense_split_repository: ExpenseSplitRepositoryInterface,
        expense_split_service: ExpenseSplitService
    ):
        self._expense_split_repository = expense_split_repository
        self._expense_split_service = expense_split_service

    async def execute(
        self, 
        expense_id: str, 
        dto: UpdateExpenseSplitsDTO, 
        user_id: str
    ) -> ExpenseSplitsResponseDTO:
        """Actualizar divisiones de un gasto"""
        
        # Validar datos
        if not dto.splits:
            raise ValidationError("Debe especificar al menos una división")

        # Convertir DTOs a datos
        splits_data = []
        for split_dto in dto.splits:
            splits_data.append({
                'user_id': split_dto.user_id,
                'amount': split_dto.amount,
                'notes': split_dto.notes
            })

        # Actualizar divisiones
        updated_splits = await self._expense_split_service.update_expense_splits(
            expense_id, splits_data
        )

        # Convertir a respuesta
        split_dtos = []
        total_amount = 0
        pending_count = 0
        paid_count = 0

        for split in updated_splits:
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