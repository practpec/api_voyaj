from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime


class CreateExpenseSplitDTO(BaseModel):
    user_id: str = Field(..., description="ID del usuario")
    amount: Decimal = Field(..., gt=0, description="Monto a pagar")
    notes: Optional[str] = Field(None, max_length=500, description="Notas adicionales")


class UpdateExpenseSplitsDTO(BaseModel):
    splits: List[CreateExpenseSplitDTO] = Field(..., min_length=1, description="Lista de divisiones")


class MarkSplitAsPaidDTO(BaseModel):
    notes: Optional[str] = Field(None, max_length=500, description="Notas del pago")


class ChangeExpenseSplitStatusDTO(BaseModel):
    status: str = Field(..., description="Nuevo estado (pending, paid, cancelled)")
    notes: Optional[str] = Field(None, max_length=500, description="Notas del cambio")


class ExpenseSplitResponseDTO(BaseModel):
    id: str
    expense_id: str
    user_id: str
    amount: Decimal
    status: str
    paid_at: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime


class ExpenseSplitsResponseDTO(BaseModel):
    expense_id: str
    total_amount: Decimal
    splits: List[ExpenseSplitResponseDTO]
    pending_count: int
    paid_count: int


class UserBalanceDTO(BaseModel):
    amount_owed: Decimal
    amount_paid: Decimal
    net_balance: Decimal
    status: str


class TripBalancesResponseDTO(BaseModel):
    trip_id: str
    user_balances: Dict[str, UserBalanceDTO]
    total_debts: Decimal
    total_credits: Decimal
    is_balanced: bool