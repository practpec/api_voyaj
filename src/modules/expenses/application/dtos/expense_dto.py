from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal
from enum import Enum


class ExpenseCategoryEnum(str, Enum):
    TRANSPORT = "transport"
    ACCOMMODATION = "accommodation"
    FOOD = "food"
    ACTIVITIES = "activities"
    SHOPPING = "shopping"
    OTHER = "other"


class ExpenseStatusEnum(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class CreateExpenseDTO(BaseModel):
    """DTO para crear gasto"""
    trip_id: str = Field(..., description="ID del viaje")
    amount: Decimal = Field(..., gt=0, le=999999.99, description="Monto del gasto")
    currency: str = Field(..., min_length=3, max_length=3, description="Código de moneda")
    category: ExpenseCategoryEnum = Field(..., description="Categoría del gasto")
    description: str = Field(..., min_length=3, max_length=500, description="Descripción")
    expense_date: datetime = Field(..., description="Fecha del gasto")
    is_shared: bool = Field(False, description="Es gasto compartido")
    paid_by_user_id: Optional[str] = Field(None, description="Usuario que pagó")
    activity_id: Optional[str] = Field(None, description="Actividad asociada")
    diary_entry_id: Optional[str] = Field(None, description="Entrada de diario asociada")
    location: Optional[str] = Field(None, max_length=200, description="Ubicación")
    receipt_url: Optional[str] = Field(None, description="URL del comprobante")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales")

    @validator('currency')
    def validate_currency(cls, v):
        return v.upper()

    @validator('amount')
    def validate_amount(cls, v):
        return round(v, 2)

    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }


class UpdateExpenseDTO(BaseModel):
    """DTO para actualizar gasto"""
    amount: Optional[Decimal] = Field(None, gt=0, le=999999.99)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    category: Optional[ExpenseCategoryEnum] = None
    description: Optional[str] = Field(None, min_length=3, max_length=500)
    expense_date: Optional[datetime] = None
    is_shared: Optional[bool] = None
    paid_by_user_id: Optional[str] = None
    activity_id: Optional[str] = None
    diary_entry_id: Optional[str] = None
    location: Optional[str] = Field(None, max_length=200)
    receipt_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    @validator('currency')
    def validate_currency(cls, v):
        return v.upper() if v else v

    @validator('amount')
    def validate_amount(cls, v):
        return round(v, 2) if v is not None else v

    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }


class ChangeExpenseStatusDTO(BaseModel):
    """DTO para cambiar estado del gasto"""
    status: ExpenseStatusEnum = Field(..., description="Nuevo estado")
    notes: Optional[str] = Field(None, max_length=500, description="Notas del cambio")


class ExpenseResponseDTO(BaseModel):
    """DTO de respuesta para gasto"""
    id: str
    trip_id: str
    user_id: str
    amount: Decimal
    currency: str
    category: ExpenseCategoryEnum
    description: str
    expense_date: datetime
    is_shared: bool
    paid_by_user_id: str
    activity_id: Optional[str] = None
    diary_entry_id: Optional[str] = None
    location: Optional[str] = None
    receipt_url: Optional[str] = None
    status: ExpenseStatusEnum
    metadata: Optional[Dict[str, Any]] = None
    can_edit: bool
    can_delete: bool
    can_change_status: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }


class ExpenseListResponseDTO(BaseModel):
    """DTO de respuesta para lista de gastos"""
    id: str
    amount: Decimal
    currency: str
    category: ExpenseCategoryEnum
    description: str
    expense_date: datetime
    is_shared: bool
    location: Optional[str] = None
    status: ExpenseStatusEnum
    can_edit: bool
    created_at: datetime

    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }


class TripExpensesResponseDTO(BaseModel):
    """DTO de respuesta para gastos del viaje"""
    trip_id: str
    expenses: List[ExpenseListResponseDTO]
    total_expenses: int
    total_amount: Decimal
    currency: str
    expenses_by_category: Dict[str, int]
    shared_expenses_count: int
    individual_expenses_count: int


class ExpenseSummaryDTO(BaseModel):
    """DTO para resumen de gastos"""
    trip_id: str
    total_amount: Decimal
    currency: str
    total_expenses: int
    by_category: Dict[str, Decimal]
    by_user: Dict[str, Decimal]
    shared_amount: Decimal
    individual_amount: Decimal
    average_per_expense: Decimal

    class Config:
        json_encoders = {
            Decimal: str
        }


class ExpenseDTOMapper:
    """Mapper para convertir entre entidades y DTOs"""
    
    @staticmethod
    def to_expense_response(
        expense_data: Any,
        can_edit: bool = False,
        can_delete: bool = False,
        can_change_status: bool = False
    ) -> ExpenseResponseDTO:
        """Convertir datos de entidad a DTO de respuesta"""
        return ExpenseResponseDTO(
            id=expense_data.id,
            trip_id=expense_data.trip_id,
            user_id=expense_data.user_id,
            amount=expense_data.amount,
            currency=expense_data.currency,
            category=expense_data.category.value,
            description=expense_data.description,
            expense_date=expense_data.expense_date,
            is_shared=expense_data.is_shared,
            paid_by_user_id=expense_data.paid_by_user_id,
            activity_id=expense_data.activity_id,
            diary_entry_id=expense_data.diary_entry_id,
            location=expense_data.location,
            receipt_url=expense_data.receipt_url,
            status=expense_data.status.value,
            metadata=expense_data.metadata,
            can_edit=can_edit,
            can_delete=can_delete,
            can_change_status=can_change_status,
            is_deleted=expense_data.is_deleted,
            created_at=expense_data.created_at,
            updated_at=expense_data.updated_at
        )

    @staticmethod
    def to_expense_list_response(expense_data: Any, can_edit: bool = False) -> ExpenseListResponseDTO:
        """Convertir datos de entidad a DTO de lista"""
        return ExpenseListResponseDTO(
            id=expense_data.id,
            amount=expense_data.amount,
            currency=expense_data.currency,
            category=expense_data.category.value,
            description=expense_data.description,
            expense_date=expense_data.expense_date,
            is_shared=expense_data.is_shared,
            location=expense_data.location,
            status=expense_data.status.value,
            can_edit=can_edit,
            created_at=expense_data.created_at
        )

    @staticmethod
    def to_trip_expenses_response(
        trip_id: str,
        expenses: List[ExpenseListResponseDTO],
        summary_data: Dict[str, Any]
    ) -> TripExpensesResponseDTO:
        """Convertir lista de gastos a respuesta del viaje"""
        return TripExpensesResponseDTO(
            trip_id=trip_id,
            expenses=expenses,
            total_expenses=len(expenses),
            total_amount=summary_data.get("total_amount", Decimal('0')),
            currency=summary_data.get("currency", "USD"),
            expenses_by_category=summary_data.get("by_category", {}),
            shared_expenses_count=summary_data.get("shared_count", 0),
            individual_expenses_count=summary_data.get("individual_count", 0)
        )