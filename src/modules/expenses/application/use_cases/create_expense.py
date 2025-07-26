from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
from ...domain.expense import Expense, ExpenseCategory
from ...domain.expense_service import ExpenseService
from ...domain.interfaces.expense_repository_interface import ExpenseRepositoryInterface
from ...domain.expense_events import ExpenseCreatedEvent
from ..dtos.create_expense_dto import CreateExpenseDTO
from shared.errors.custom_errors import ValidationError, NotFoundError
from shared.events.event_bus import EventBus


class CreateExpense:
    def __init__(
        self, 
        expense_repository: ExpenseRepositoryInterface,
        expense_service: ExpenseService,
        event_bus: EventBus
    ):
        self._expense_repository = expense_repository
        self._expense_service = expense_service
        self._event_bus = event_bus

    async def execute(self, dto: CreateExpenseDTO, user_id: str) -> Dict[str, Any]:
        """Crear nuevo gasto"""
        
        # Validar monto y moneda
        await self._expense_service.validate_expense_amount_limits(dto.amount, dto.currency)

        # Crear entidad de gasto
        expense = Expense.create(
            trip_id=dto.trip_id,
            user_id=user_id,
            amount=dto.amount,
            currency=dto.currency,
            category=ExpenseCategory(dto.category),
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
        await self._expense_repository.save(expense)

        # Publicar evento
        event = ExpenseCreatedEvent(
            expense_id=expense.id,
            trip_id=expense.trip_id,
            user_id=user_id,
            amount=expense.amount,
            currency=expense.currency,
            category=expense.category.value,
            is_shared=expense.is_shared,
            activity_id=expense._data.activity_id,
            diary_entry_id=expense._data.diary_entry_id
        )
        await self._event_bus.publish(event)

        return {
            "success": True,
            "message": "Gasto creado exitosamente",
            "data": {
                "expense_id": expense.id,
                "amount": float(expense.amount),
                "currency": expense.currency,
                "category": expense.category.value,
                "description": expense._data.description,
                "is_shared": expense.is_shared,
                "requires_receipt": await self._expense_service.should_require_receipt(expense),
                "created_at": expense._data.created_at.isoformat()
            }
        }