from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List
from decimal import Decimal
import uuid
from enum import Enum
from shared.errors.custom_errors import ValidationError


class ExpenseCategory(Enum):
    TRANSPORTATION = "transportation"
    ACCOMMODATION = "accommodation"
    FOOD = "food"
    ACTIVITIES = "activities"
    SHOPPING = "shopping"
    HEALTHCARE = "healthcare"
    COMMUNICATION = "communication"
    INSURANCE = "insurance"
    EMERGENCY = "emergency"
    OTHER = "other"


class ExpenseStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


@dataclass
class ExpenseData:
    id: str
    trip_id: str
    user_id: str
    activity_id: Optional[str]
    diary_entry_id: Optional[str]
    amount: Decimal
    currency: str
    category: ExpenseCategory
    description: str
    receipt_url: Optional[str]
    location: Optional[str]
    expense_date: datetime
    is_shared: bool
    paid_by_user_id: str
    status: ExpenseStatus
    metadata: Optional[Dict[str, Any]]
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


class Expense:
    def __init__(self, data: ExpenseData):
        self._data = data
        self._validate()

    @classmethod
    def create(
        cls,
        trip_id: str,
        user_id: str,
        amount: Decimal,
        currency: str,
        category: ExpenseCategory,
        description: str,
        expense_date: datetime,
        is_shared: bool = False,
        paid_by_user_id: Optional[str] = None,
        activity_id: Optional[str] = None,
        diary_entry_id: Optional[str] = None,
        location: Optional[str] = None,
        receipt_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'Expense':
        """Crear nuevo gasto"""
        if amount <= 0:
            raise ValidationError("El monto debe ser mayor a cero")

        if not description or len(description.strip()) < 3:
            raise ValidationError("La descripción debe tener al menos 3 caracteres")

        if len(description) > 500:
            raise ValidationError("La descripción no puede exceder 500 caracteres")

        if not currency or len(currency) != 3:
            raise ValidationError("La moneda debe ser un código ISO de 3 letras")

        # Si no se especifica quién pagó, por defecto es quien registra el gasto
        if not paid_by_user_id:
            paid_by_user_id = user_id

        data = ExpenseData(
            id=str(uuid.uuid4()),
            trip_id=trip_id,
            user_id=user_id,
            activity_id=activity_id,
            diary_entry_id=diary_entry_id,
            amount=amount,
            currency=currency.upper(),
            category=category,
            description=description.strip(),
            receipt_url=receipt_url,
            location=location,
            expense_date=expense_date,
            is_shared=is_shared,
            paid_by_user_id=paid_by_user_id,
            status=ExpenseStatus.PENDING,
            metadata=metadata or {},
            is_deleted=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        return cls(data)

    def update_amount(self, new_amount: Decimal) -> None:
        """Actualizar monto del gasto"""
        if new_amount <= 0:
            raise ValidationError("El monto debe ser mayor a cero")

        self._data.amount = new_amount
        self._data.updated_at = datetime.utcnow()

    def update_description(self, new_description: str) -> None:
        """Actualizar descripción"""
        if not new_description or len(new_description.strip()) < 3:
            raise ValidationError("La descripción debe tener al menos 3 caracteres")

        if len(new_description) > 500:
            raise ValidationError("La descripción no puede exceder 500 caracteres")

        self._data.description = new_description.strip()
        self._data.updated_at = datetime.utcnow()

    def update_category(self, new_category: ExpenseCategory) -> None:
        """Actualizar categoría"""
        self._data.category = new_category
        self._data.updated_at = datetime.utcnow()

    def attach_receipt(self, receipt_url: str) -> None:
        """Adjuntar comprobante"""
        if not receipt_url or not receipt_url.startswith(('http://', 'https://')):
            raise ValidationError("URL del comprobante inválida")

        self._data.receipt_url = receipt_url
        self._data.updated_at = datetime.utcnow()

    def remove_receipt(self) -> None:
        """Remover comprobante"""
        self._data.receipt_url = None
        self._data.updated_at = datetime.utcnow()

    def set_location(self, location: str) -> None:
        """Establecer ubicación del gasto"""
        if location and len(location) > 200:
            raise ValidationError("La ubicación no puede exceder 200 caracteres")

        self._data.location = location.strip() if location else None
        self._data.updated_at = datetime.utcnow()

    def confirm(self) -> None:
        """Confirmar el gasto"""
        self._data.status = ExpenseStatus.CONFIRMED
        self._data.updated_at = datetime.utcnow()

    def cancel(self) -> None:
        """Cancelar el gasto"""
        self._data.status = ExpenseStatus.CANCELLED
        self._data.updated_at = datetime.utcnow()

    def associate_with_activity(self, activity_id: str) -> None:
        """Asociar gasto con actividad"""
        self._data.activity_id = activity_id
        self._data.updated_at = datetime.utcnow()

    def associate_with_diary_entry(self, diary_entry_id: str) -> None:
        """Asociar gasto con entrada de diario"""
        self._data.diary_entry_id = diary_entry_id
        self._data.updated_at = datetime.utcnow()

    def make_shared(self) -> None:
        """Hacer el gasto compartido"""
        self._data.is_shared = True
        self._data.updated_at = datetime.utcnow()

    def make_individual(self) -> None:
        """Hacer el gasto individual"""
        self._data.is_shared = False
        self._data.updated_at = datetime.utcnow()

    def change_payer(self, new_payer_user_id: str) -> None:
        """Cambiar quién pagó el gasto"""
        self._data.paid_by_user_id = new_payer_user_id
        self._data.updated_at = datetime.utcnow()

    def update_metadata(self, metadata: Dict[str, Any]) -> None:
        """Actualizar metadatos"""
        self._data.metadata = metadata or {}
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

    def can_be_edited_by(self, user_id: str) -> bool:
        """Verificar si el usuario puede editar el gasto"""
        return (self._data.user_id == user_id or self._data.paid_by_user_id == user_id) and self.is_active()

    def can_be_split(self) -> bool:
        """Verificar si el gasto puede ser dividido"""
        return self._data.is_shared and self._data.status == ExpenseStatus.CONFIRMED

    def get_category_display(self) -> str:
        """Obtener nombre de categoría para mostrar"""
        category_names = {
            ExpenseCategory.TRANSPORTATION: "Transporte",
            ExpenseCategory.ACCOMMODATION: "Alojamiento", 
            ExpenseCategory.FOOD: "Comida",
            ExpenseCategory.ACTIVITIES: "Actividades",
            ExpenseCategory.SHOPPING: "Compras",
            ExpenseCategory.HEALTHCARE: "Salud",
            ExpenseCategory.COMMUNICATION: "Comunicación",
            ExpenseCategory.INSURANCE: "Seguros",
            ExpenseCategory.EMERGENCY: "Emergencia",
            ExpenseCategory.OTHER: "Otros"
        }
        return category_names.get(self._data.category, "Otros")

    def to_public_data(self) -> ExpenseData:
        """Obtener datos públicos del gasto"""
        return self._data

    @property
    def id(self) -> str:
        return self._data.id

    @property
    def trip_id(self) -> str:
        return self._data.trip_id

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

    @property
    def status(self) -> ExpenseStatus:
        return self._data.status

    def _validate(self) -> None:
        """Validar datos del gasto"""
        if not self._data.id:
            raise ValidationError("ID del gasto es requerido")

        if not self._data.trip_id:
            raise ValidationError("ID del viaje es requerido")

        if not self._data.user_id:
            raise ValidationError("ID del usuario es requerido")

        if not self._data.paid_by_user_id:
            raise ValidationError("ID del usuario que pagó es requerido")

        if self._data.amount <= 0:
            raise ValidationError("El monto debe ser mayor a cero")

        if not self._data.currency or len(self._data.currency) != 3:
            raise ValidationError("Moneda inválida")

        if not self._data.description:
            raise ValidationError("Descripción es requerida")