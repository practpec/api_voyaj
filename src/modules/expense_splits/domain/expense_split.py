from typing import Optional
from datetime import datetime
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from shared.errors.custom_errors import ValidationError


class ExpenseSplitStatus(Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"


@dataclass
class ExpenseSplitData:
    id: str
    expense_id: str
    user_id: str
    amount: Decimal
    status: ExpenseSplitStatus = ExpenseSplitStatus.PENDING
    paid_at: Optional[datetime] = None
    notes: Optional[str] = None
    is_deleted: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ExpenseSplit:
    def __init__(self, data: ExpenseSplitData):
        self._data = data
        if self._data.created_at is None:
            self._data.created_at = datetime.utcnow()
        if self._data.updated_at is None:
            self._data.updated_at = datetime.utcnow()
        self._validate()

    def _validate(self) -> None:
        """Validar datos de la división"""
        if not self._data.expense_id:
            raise ValidationError("El ID del gasto es requerido")
        
        if not self._data.user_id:
            raise ValidationError("El ID del usuario es requerido")
        
        if self._data.amount <= 0:
            raise ValidationError("El monto debe ser mayor a cero")

    # Getters
    @property
    def id(self) -> str:
        return self._data.id
    
    @property
    def expense_id(self) -> str:
        return self._data.expense_id
    
    @property
    def user_id(self) -> str:
        return self._data.user_id
    
    @property
    def amount(self) -> Decimal:
        return self._data.amount
    
    @property
    def status(self) -> ExpenseSplitStatus:
        return self._data.status
    
    @property
    def paid_at(self) -> Optional[datetime]:
        return self._data.paid_at
    
    @property
    def notes(self) -> Optional[str]:
        return self._data.notes
    
    @property
    def created_at(self) -> datetime:
        return self._data.created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._data.updated_at

    # Métodos de negocio
    def is_active(self) -> bool:
        """Verificar si la división está activa"""
        return not self._data.is_deleted

    def is_paid(self) -> bool:
        """Verificar si está pagado"""
        return self._data.status == ExpenseSplitStatus.PAID

    def is_pending(self) -> bool:
        """Verificar si está pendiente"""
        return self._data.status == ExpenseSplitStatus.PENDING

    def mark_as_paid(self, notes: Optional[str] = None) -> None:
        """Marcar como pagado"""
        self._data.status = ExpenseSplitStatus.PAID
        self._data.paid_at = datetime.utcnow()
        if notes:
            self._data.notes = notes.strip()
        self._data.updated_at = datetime.utcnow()

    def mark_as_pending(self) -> None:
        """Marcar como pendiente"""
        self._data.status = ExpenseSplitStatus.PENDING
        self._data.paid_at = None
        self._data.updated_at = datetime.utcnow()

    def cancel(self) -> None:
        """Cancelar división"""
        self._data.status = ExpenseSplitStatus.CANCELLED
        self._data.paid_at = None
        self._data.updated_at = datetime.utcnow()

    def is_cancelled(self) -> bool:
        """Verificar si está cancelado"""
        return self._data.status == ExpenseSplitStatus.CANCELLED

    def update_amount(self, amount: Decimal) -> None:
        """Actualizar monto"""
        if amount <= 0:
            raise ValidationError("El monto debe ser mayor a cero")
        
        self._data.amount = amount
        self._data.updated_at = datetime.utcnow()

    def add_notes(self, notes: str) -> None:
        """Agregar notas"""
        self._data.notes = notes.strip() if notes else None
        self._data.updated_at = datetime.utcnow()

    def soft_delete(self) -> None:
        """Eliminación suave"""
        self._data.is_deleted = True
        self._data.updated_at = datetime.utcnow()

    def restore(self) -> None:
        """Restaurar división eliminada"""
        self._data.is_deleted = False
        self._data.updated_at = datetime.utcnow()

    def to_public_data(self) -> ExpenseSplitData:
        """Convertir a datos públicos"""
        return self._data