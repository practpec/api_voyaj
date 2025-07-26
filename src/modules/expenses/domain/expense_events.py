from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from shared.events.base_event import BaseEvent


@dataclass
class ExpenseCreatedEvent(BaseEvent):
    """Evento cuando se crea un gasto"""
    expense_id: str
    trip_id: str
    user_id: str
    amount: Decimal
    currency: str
    category: str
    is_shared: bool
    activity_id: Optional[str] = None
    diary_entry_id: Optional[str] = None

    def __post_init__(self):
        super().__init__()
        self.event_type = "expense.created"


@dataclass
class ExpenseUpdatedEvent(BaseEvent):
    """Evento cuando se actualiza un gasto"""
    expense_id: str
    trip_id: str
    user_id: str
    updated_fields: Dict[str, Any]
    previous_amount: Optional[Decimal] = None
    new_amount: Optional[Decimal] = None

    def __post_init__(self):
        super().__init__()
        self.event_type = "expense.updated"


@dataclass
class ExpenseDeletedEvent(BaseEvent):
    """Evento cuando se elimina un gasto"""
    expense_id: str
    trip_id: str
    user_id: str
    amount: Decimal
    currency: str

    def __post_init__(self):
        super().__init__()
        self.event_type = "expense.deleted"


@dataclass
class ExpenseConfirmedEvent(BaseEvent):
    """Evento cuando se confirma un gasto"""
    expense_id: str
    trip_id: str
    user_id: str
    amount: Decimal
    currency: str
    is_shared: bool

    def __post_init__(self):
        super().__init__()
        self.event_type = "expense.confirmed"


@dataclass
class ExpenseReceiptUploadedEvent(BaseEvent):
    """Evento cuando se sube comprobante"""
    expense_id: str
    trip_id: str
    user_id: str
    receipt_url: str

    def __post_init__(self):
        super().__init__()
        self.event_type = "expense.receipt_uploaded"


@dataclass
class ExpenseBudgetExceededEvent(BaseEvent):
    """Evento cuando gastos exceden presupuesto"""
    trip_id: str
    total_expenses: Decimal
    budget_limit: Decimal
    currency: str
    exceeded_by: Decimal

    def __post_init__(self):
        super().__init__()
        self.event_type = "expense.budget_exceeded"


@dataclass
class ExpenseSharedEvent(BaseEvent):
    """Evento cuando un gasto se hace compartido"""
    expense_id: str
    trip_id: str
    user_id: str
    amount: Decimal
    currency: str

    def __post_init__(self):
        super().__init__()
        self.event_type = "expense.made_shared"


@dataclass
class ExpenseAssociatedWithActivityEvent(BaseEvent):
    """Evento cuando gasto se asocia con actividad"""
    expense_id: str
    trip_id: str
    activity_id: str
    user_id: str

    def __post_init__(self):
        super().__init__()
        self.event_type = "expense.associated_with_activity"


@dataclass
class ExpenseAssociatedWithDiaryEvent(BaseEvent):
    """Evento cuando gasto se asocia con entrada de diario"""
    expense_id: str
    trip_id: str
    diary_entry_id: str
    user_id: str

    def __post_init__(self):
        super().__init__()
        self.event_type = "expense.associated_with_diary"