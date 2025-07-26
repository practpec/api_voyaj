from ..dtos.expense_dto import ExpenseSummaryDTO
from ...domain.expense_service import ExpenseService
from ...domain.interfaces.expense_repository_interface import ExpenseRepositoryInterface
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from shared.errors.custom_errors import ForbiddenError


class GetExpenseSummaryUseCase:
    def __init__(
        self,
        expense_repository: ExpenseRepositoryInterface,
        expense_service: ExpenseService,
        trip_member_repository: ITripMemberRepository
    ):
        self._expense_repository = expense_repository
        self._expense_service = expense_service
        self._trip_member_repository = trip_member_repository

    async def execute(self, trip_id: str, user_id: str) -> ExpenseSummaryDTO:
        """Obtener resumen de gastos del viaje"""
        
        # Validar permisos
        trip_member = await self._trip_member_repository.find_by_trip_and_user(trip_id, user_id)
        if not trip_member or not trip_member.is_active():
            raise ForbiddenError("No tienes permisos para ver el resumen de este viaje")

        # Obtener resumen
        summary_data = await self._expense_service.get_detailed_expense_summary(trip_id)

        return ExpenseSummaryDTO(
            trip_id=trip_id,
            total_amount=summary_data["total_amount"],
            currency=summary_data["currency"],
            total_expenses=summary_data["total_expenses"],
            by_category=summary_data["by_category"],
            by_user=summary_data["by_user"],
            shared_amount=summary_data["shared_amount"],
            individual_amount=summary_data["individual_amount"],
            average_per_expense=summary_data["average_per_expense"]
        )