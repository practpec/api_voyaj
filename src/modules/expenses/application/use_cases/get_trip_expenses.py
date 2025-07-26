from typing import Optional
from ..dtos.expense_dto import TripExpensesResponseDTO, ExpenseListResponseDTO, ExpenseDTOMapper
from ...domain.expense_service import ExpenseService
from ...domain.interfaces.expense_repository_interface import ExpenseRepositoryInterface
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from shared.errors.custom_errors import NotFoundError, ForbiddenError


class GetTripExpensesUseCase:
    def __init__(
        self,
        expense_repository: ExpenseRepositoryInterface,
        expense_service: ExpenseService,
        trip_member_repository: ITripMemberRepository
    ):
        self._expense_repository = expense_repository
        self._expense_service = expense_service
        self._trip_member_repository = trip_member_repository

    async def execute(
        self, trip_id: str, user_id: str, category: Optional[str] = None
    ) -> TripExpensesResponseDTO:
        """Obtener gastos de un viaje"""
        
        # Validar permisos del usuario
        await self._validate_user_permissions(trip_id, user_id)

        # Obtener gastos del viaje
        expenses = await self._expense_repository.find_by_trip_id(trip_id, category)
        
        # Convertir a DTOs de lista
        expense_list_responses = []
        for expense in expenses:
            if not expense.is_active():
                continue
                
            can_edit = expense.user_id == user_id
            
            expense_response = ExpenseDTOMapper.to_expense_list_response(
                expense.to_public_data(),
                can_edit=can_edit
            )
            expense_list_responses.append(expense_response)

        # Obtener datos de resumen
        summary_data = await self._expense_service.get_trip_expense_summary(trip_id)

        # Crear respuesta completa
        return ExpenseDTOMapper.to_trip_expenses_response(
            trip_id=trip_id,
            expenses=expense_list_responses,
            summary_data=summary_data
        )

    async def _validate_user_permissions(self, trip_id: str, user_id: str) -> None:
        """Validar que el usuario tenga permisos para ver gastos del viaje"""
        trip_member = await self._trip_member_repository.find_by_trip_and_user(trip_id, user_id)
        if not trip_member or not trip_member.is_active():
            raise ForbiddenError("No tienes permisos para ver los gastos de este viaje")