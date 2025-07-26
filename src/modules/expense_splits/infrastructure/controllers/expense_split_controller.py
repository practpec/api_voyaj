from typing import Optional
from ...application.dtos.expense_split_dto import (
    UpdateExpenseSplitsDTO, MarkSplitAsPaidDTO, ChangeExpenseSplitStatusDTO,
    ExpenseSplitsResponseDTO, ExpenseSplitResponseDTO, TripBalancesResponseDTO
)
from ...application.use_cases.get_expense_splits import GetExpenseSplitsUseCase
from ...application.use_cases.update_expense_splits import UpdateExpenseSplitsUseCase
from ...application.use_cases.mark_split_as_paid import MarkSplitAsPendingUseCase
from ...application.use_cases.change_split_status import ChangeSplitStatusUseCase
from ...application.use_cases.get_trip_balances import GetTripBalancesUseCase
from shared.utils.response_utils import SuccessResponse


class ExpenseSplitController:
    def __init__(
        self,
        get_expense_splits_use_case: GetExpenseSplitsUseCase,
        update_expense_splits_use_case: UpdateExpenseSplitsUseCase,
        mark_split_as_paid_use_case: MarkSplitAsPendingUseCase,
        change_split_status_use_case: ChangeSplitStatusUseCase,
        get_trip_balances_use_case: GetTripBalancesUseCase
    ):
        self._get_expense_splits_use_case = get_expense_splits_use_case
        self._update_expense_splits_use_case = update_expense_splits_use_case
        self._mark_split_as_paid_use_case = mark_split_as_paid_use_case
        self._change_split_status_use_case = change_split_status_use_case
        self._get_trip_balances_use_case = get_trip_balances_use_case

    async def get_expense_splits(self, expense_id: str, current_user: dict) -> SuccessResponse:
        """Obtener divisiones de un gasto"""
        result = await self._get_expense_splits_use_case.execute(
            expense_id, current_user["id"]
        )
        return SuccessResponse(
            message="Divisiones obtenidas exitosamente",
            data=result
        )

    async def update_expense_splits(
        self, 
        expense_id: str, 
        dto: UpdateExpenseSplitsDTO, 
        current_user: dict
    ) -> SuccessResponse:
        """Actualizar divisiones de un gasto"""
        result = await self._update_expense_splits_use_case.execute(
            expense_id, dto, current_user["id"]
        )
        return SuccessResponse(
            message="Divisiones actualizadas exitosamente",
            data=result
        )

    async def mark_split_as_paid(
        self, 
        expense_split_id: str, 
        dto: MarkSplitAsPaidDTO, 
        current_user: dict
    ) -> SuccessResponse:
        """Marcar división como pagada"""
        result = await self._mark_split_as_paid_use_case.execute(
            expense_split_id, dto, current_user["id"]
        )
        return SuccessResponse(
            message="División marcada como pagada",
            data=result
        )

    async def change_split_status(
        self, 
        expense_split_id: str, 
        dto: ChangeExpenseSplitStatusDTO, 
        current_user: dict
    ) -> SuccessResponse:
        """Cambiar estado de una división"""
        result = await self._change_split_status_use_case.execute(
            expense_split_id, dto, current_user["id"]
        )
        return SuccessResponse(
            message=f"Estado cambiado a {dto.status}",
            data=result
        )

    async def get_trip_balances(self, trip_id: str, current_user: dict) -> SuccessResponse:
        """Obtener balances de usuarios en un viaje"""
        result = await self._get_trip_balances_use_case.execute(
            trip_id, current_user["id"]
        )
        return SuccessResponse(
            message="Balances obtenidos exitosamente",
            data=result
        )

    async def health_check(self) -> SuccessResponse:
        """Health check del módulo"""
        return SuccessResponse(
            message="Módulo expense_splits funcionando correctamente",
            data={"status": "healthy", "module": "expense_splits"}
        )