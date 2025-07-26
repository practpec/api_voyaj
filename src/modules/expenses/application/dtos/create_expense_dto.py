from dataclasses import dataclass
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime


@dataclass
class CreateExpenseDTO:
    """DTO para crear gasto"""
    trip_id: str
    amount: Decimal
    currency: str
    category: str
    description: str
    expense_date: datetime
    is_shared: bool = False
    paid_by_user_id: Optional[str] = None
    activity_id: Optional[str] = None
    diary_entry_id: Optional[str] = None
    location: Optional[str] = None
    receipt_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validaciones básicas del DTO"""
        if not self.trip_id:
            raise ValueError("trip_id es requerido")
        
        if self.amount <= 0:
            raise ValueError("amount debe ser mayor a cero")
        
        if not self.currency or len(self.currency) != 3:
            raise ValueError("currency debe ser código ISO de 3 letras")
        
        if not self.category:
            raise ValueError("category es requerido")
        
        if not self.description or len(self.description.strip()) < 3:
            raise ValueError("description debe tener al menos 3 caracteres")
        
        if not self.expense_date:
            raise ValueError("expense_date es requerido")

        # Normalizar datos
        self.currency = self.currency.upper()
        self.description = self.description.strip()
        if self.location:
            self.location = self.location.strip()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CreateExpenseDTO':
        """Crear DTO desde diccionario"""
        return cls(
            trip_id=data.get("trip_id"),
            amount=Decimal(str(data.get("amount", 0))),
            currency=data.get("currency"),
            category=data.get("category"),
            description=data.get("description"),
            expense_date=data.get("expense_date"),
            is_shared=data.get("is_shared", False),
            paid_by_user_id=data.get("paid_by_user_id"),
            activity_id=data.get("activity_id"),
            diary_entry_id=data.get("diary_entry_id"),
            location=data.get("location"),
            receipt_url=data.get("receipt_url"),
            metadata=data.get("metadata")
        )