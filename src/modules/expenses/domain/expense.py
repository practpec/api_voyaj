from typing import Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from shared.errors.custom_errors import ValidationError


class ExpenseCategory(Enum):
    TRANSPORT = "transport"
    ACCOMMODATION = "accommodation"
    FOOD = "food"
    ACTIVITIES = "activities"
    SHOPPING = "shopping"
    OTHER = "other"


class ExpenseStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class ExpenseData:
    id: str
    trip_id: str
    user_id: str
    amount: Decimal
    currency: str
    category: ExpenseCategory
    description: str
    expense_date: datetime
    is_shared: bool
    paid_by_user_id: str
    activity_id: Optional[str] = None
    diary_entry_id: Optional[str] = None
    location: Optional[str] = None
    receipt_url: Optional[str] = None
    status: ExpenseStatus = ExpenseStatus.PENDING
    metadata: Optional[Dict[str, Any]] = None
    is_deleted: bool = False
    created_at: datetime = None
    updated_at: datetime = None


class Expense:
    def __init__(self, data: ExpenseData):
        self._data = data
        if self._data.created_at is None:
            self._data.created_at = datetime.utcnow()
        if self._data.updated_at is None:
            self._data.updated_at = datetime.utcnow()
        self._validate()

    def _validate(self) -> None:
        """Validar datos del gasto"""
        if not self._data.trip_id:
            raise ValidationError("El ID del viaje es requerido")
        
        if not self._data.user_id:
            raise ValidationError("El ID del usuario es requerido")
        
        if self._data.amount <= 0:
            raise ValidationError("El monto debe ser mayor a cero")
        
        if self._data.amount > Decimal('999999.99'):
            raise ValidationError("El monto no puede ser mayor a 999,999.99")
        
        if not self._data.currency or len(self._data.currency) != 3:
            raise ValidationError("La moneda debe ser un código ISO de 3 letras")
        
        if not self._data.description or len(self._data.description.strip()) < 3:
            raise ValidationError("La descripción debe tener al menos 3 caracteres")

    @property
    def id(self) -> str:
        return self._data.id

    @property
    def trip_id(self) -> str:
        return self._data.trip_id

    @property
    def user_id(self) -> str:
        return self._data.user_id

    @property
    def amount(self) -> Decimal:
        return self._data.amount

    @property
    def currency(self) -> str:
        return self._data.currency

    @property
    def category(self) -> ExpenseCategory:
        return self._data.category

    @property
    def is_shared(self) -> bool:
        return self._data.is_shared

    def update_amount(self, new_amount: Decimal) -> None:
        """Actualizar monto del gasto"""
        if new_amount <= 0:
            raise ValidationError("El monto debe ser mayor a cero")
        
        if new_amount > Decimal('999999.99'):
            raise ValidationError("El monto no puede ser mayor a 999,999.99")
        
        self._data.amount = new_amount
        self._data.updated_at = datetime.utcnow()

    def update_currency(self, currency: str) -> None:
        """Actualizar moneda del gasto"""
        if not currency or len(currency) != 3:
            raise ValidationError("La moneda debe ser un código ISO de 3 letras")
        self._data.currency = currency.upper()
        self._data.updated_at = datetime.utcnow()

    def update_category(self, category: str) -> None:
        """Actualizar categoría del gasto"""
        self._data.category = ExpenseCategory(category)
        self._data.updated_at = datetime.utcnow()

    def update_description(self, description: str) -> None:
        """Actualizar descripción del gasto"""
        if not description or len(description.strip()) < 3:
            raise ValidationError("La descripción debe tener al menos 3 caracteres")
        
        self._data.description = description.strip()
        self._data.updated_at = datetime.utcnow()

    def update_expense_date(self, expense_date: datetime) -> None:
        """Actualizar fecha del gasto"""
        self._data.expense_date = expense_date
        self._data.updated_at = datetime.utcnow()

    def make_shared(self) -> None:
        """Convertir en gasto compartido"""
        self._data.is_shared = True
        self._data.updated_at = datetime.utcnow()

    def make_individual(self) -> None:
        """Convertir en gasto individual"""
        self._data.is_shared = False
        self._data.updated_at = datetime.utcnow()

    def change_payer(self, paid_by_user_id: str) -> None:
        """Cambiar quién pagó el gasto"""
        self._data.paid_by_user_id = paid_by_user_id
        self._data.updated_at = datetime.utcnow()

    def associate_with_activity(self, activity_id: str) -> None:
        """Asociar con actividad"""
        self._data.activity_id = activity_id
        self._data.updated_at = datetime.utcnow()

    def associate_with_diary_entry(self, diary_entry_id: str) -> None:
        """Asociar con entrada de diario"""
        self._data.diary_entry_id = diary_entry_id
        self._data.updated_at = datetime.utcnow()

    def set_location(self, location: str) -> None:
        """Establecer ubicación del gasto"""
        self._data.location = location.strip() if location else None
        self._data.updated_at = datetime.utcnow()

    def set_receipt_url(self, receipt_url: str) -> None:
        """Establecer URL del comprobante"""
        self._data.receipt_url = receipt_url
        self._data.updated_at = datetime.utcnow()

    def update_metadata(self, metadata: Dict[str, Any]) -> None:
        """Actualizar metadatos"""
        self._data.metadata = metadata
        self._data.updated_at = datetime.utcnow()

    def change_status(self, status: str) -> None:
        """Cambiar estado del gasto"""
        self._data.status = ExpenseStatus(status)
        self._data.updated_at = datetime.utcnow()

    def add_status_note(self, note: str) -> None:
        """Agregar nota de estado"""
        if not self._data.metadata:
            self._data.metadata = {}
        if "status_notes" not in self._data.metadata:
            self._data.metadata["status_notes"] = []
        
        self._data.metadata["status_notes"].append({
            "note": note,
            "timestamp": datetime.utcnow().isoformat()
        })
        self._data.updated_at = datetime.utcnow()

    def soft_delete(self) -> None:
        """Eliminación suave del gasto"""
        self._data.is_deleted = True
        self._data.updated_at = datetime.utcnow()

    def restore(self) -> None:
        """Restaurar gasto eliminado"""
        self._data.is_deleted = False
        self._data.updated_at = datetime.utcnow()

    def is_active(self) -> bool:
        """Verificar si el gasto está activo"""
        return not self._data.is_deleted

    def can_be_modified(self) -> bool:
        """Verificar si el gasto puede ser modificado"""
        return self.is_active() and self._data.status == ExpenseStatus.PENDING

    def get_days_since_created(self) -> int:
        """Obtener días desde la creación"""
        delta = datetime.utcnow() - self._data.created_at
        return delta.days

    def is_recent(self, days_limit: int = 7) -> bool:
        """Verificar si el gasto es reciente"""
        return self.get_days_since_created() <= days_limit

    def to_public_data(self) -> ExpenseData:
        """Obtener datos públicos del gasto"""
        return self._data

    @staticmethod
    def create(
        trip_id: str,
        user_id: str,
        amount: Decimal,
        currency: str,
        category: str,
        description: str,
        expense_date: datetime,
        is_shared: bool = False,
        paid_by_user_id: Optional[str] = None,
        activity_id: Optional[str] = None,
        diary_entry_id: Optional[str] = None,
        location: Optional[str] = None,
        receipt_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        expense_id: Optional[str] = None
    ) -> "Expense":
        """Crear nuevo gasto"""
        from uuid import uuid4
        
        data = ExpenseData(
            id=expense_id or str(uuid4()),
            trip_id=trip_id,
            user_id=user_id,
            amount=amount,
            currency=currency.upper(),
            category=ExpenseCategory(category),
            description=description.strip(),
            expense_date=expense_date,
            is_shared=is_shared,
            paid_by_user_id=paid_by_user_id or user_id,
            activity_id=activity_id,
            diary_entry_id=diary_entry_id,
            location=location.strip() if location else None,
            receipt_url=receipt_url,
            status=ExpenseStatus.PENDING,
            metadata=metadata or {},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        return Expense(data)