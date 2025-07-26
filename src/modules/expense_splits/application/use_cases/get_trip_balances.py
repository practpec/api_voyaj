from ..dtos.expense_split_dto import TripBalancesResponseDTO, UserBalanceDTO
from ...domain.interfaces.expense_split_repository_interface import ExpenseSplitRepositoryInterface
from ...domain.expense_split_service import ExpenseSplitService


class GetTripBalancesUseCase:
    def __init__(
        self,
        expense_split_repository: ExpenseSplitRepositoryInterface,
        expense_split_service: ExpenseSplitService
    ):
        self._expense_split_repository = expense_split_repository
        self._expense_split_service = expense_split_service

    async def execute(self, trip_id: str, user_id: str) -> TripBalancesResponseDTO:
        """Obtener balances de usuarios en un viaje"""
        
        # Calcular balances
        balances_data = await self._expense_split_service.calculate_trip_balances(trip_id)
        
        # Convertir a DTOs
        user_balances_dto = {}
        for user_id_key, balance in balances_data['user_balances'].items():
            user_balances_dto[user_id_key] = UserBalanceDTO(
                amount_owed=balance['amount_owed'],
                amount_paid=balance['amount_paid'],
                net_balance=balance['net_balance'],
                status=balance['status']
            )

        return TripBalancesResponseDTO(
            trip_id=trip_id,
            user_balances=user_balances_dto,
            total_debts=balances_data['total_debts'],
            total_credits=balances_data['total_credits'],
            is_balanced=balances_data['is_balanced']
        )