from typing import Optional, Dict, Any
from decimal import Decimal
from ...domain.expense import Expense, ExpenseCategory
from ...domain.expense_service import ExpenseService
from ...domain.interfaces.expense_repository_interface import ExpenseRepositoryInterface
from ...domain.expense_events import ExpenseUpdatedEvent
from ..dtos.update_expense_dto import UpdateExpenseDTO
from shared.errors.custom_errors import ValidationError, NotFoundError, AuthorizationError
from shared.events.event_bus import EventBus


class UpdateExpense:
    def __init__(
        self, 
        expense_repository: ExpenseRepositoryInterface,
        expense_service: ExpenseService,
        event_bus: EventBus
    ):
        self._expense_repository = expense_repository
        self._expense_service = expense_service
        self._event_bus = event_bus

    async def execute(self, expense_id: str, dto: UpdateExpenseDTO, user_id: str) -> Dict[str, Any]:
        """Actualizar gasto existente"""
        
        # Buscar gasto
        expense = await self._expense_repository.find_by_id(expense_id)
        if not expense:
            raise NotFoundError("Gasto no encontrado")

        # Validar permisos
        await self._expense_service.validate_expense_permissions(expense, user_id)

        # Guardar valores anteriores para el evento
        previous_amount = expense.amount
        updated_fields = {}

        # Actualizar campos si se proporcionan
        if dto.amount is not None:
            if dto.currency:
                await self._expense_service.validate_expense_amount_limits(dto.amount, dto.currency)
            expense.update_amount(dto.amount)
            updated_fields["amount"] = float(dto.amount)

        if dto.description is not None:
            expense.update_description(dto.description)
            updated_fields["description"] = dto.description

        if dto.category is not None:
            expense.update_category(ExpenseCategory(dto.category))
            updated_fields["category"] = dto.category

        if dto.location is not None:
            expense.set_location(dto.location)
            updated_fields["location"] = dto.location

        if dto.is_shared is not None:
            if dto.is_shared:
                expense.make_shared()
            else:
                expense.make_individual()
            updated_fields["is_shared"] = dto.is_shared

        if dto.paid_by_user_id is not None:
            expense.change_payer(dto.paid_by_user_id)
            updated_fields["paid_by_user_id"] = dto.paid_by_user_id

        if dto.activity_id is not None:
            expense.associate_with_activity(dto.activity_id)
            updated_fields["activity_id"] = dto.activity_id

        if dto.diary_entry_id is not None:
            expense.associate_with_diary_entry(dto.diary_entry_id)
            updated_fields["diary_entry_id"] = dto.diary_entry_id

        if dto.metadata is not None:
            expense.update_metadata(dto.metadata)
            updated_fields["metadata"] = dto.metadata

        # Guardar cambios
        await self._expense_repository.update(expense)

        # Publicar evento
        event = ExpenseUpdatedEvent(
            expense_id=expense.id,
            trip_id=expense.trip_id,
            user_id=user_id,
            updated_fields=updated_fields,
            previous_amount=previous_amount,
            new_amount=expense.amount
        )
        await self._event_bus.publish(event)

        return {
            "success": True,
            "message": "Gasto actualizado exitosamente",
            "data": {
                "expense_id": expense.id,
                "amount": float(expense.amount),
                "currency": expense.currency,
                "category": expense.category.value,
                "description": expense._data.description,
                "is_shared": expense.is_shared,
                "updated_fields": list(updated_fields.keys()),
                "updated_at": expense._data.updated_at.isoformat()
            }
        }