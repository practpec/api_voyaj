from dataclasses import dataclass
from typing import Optional, Dict, Any
from decimal import Decimal


@dataclass
class UpdateExpenseDTO:
    """DTO para actualizar gasto"""
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    is_shared: Optional[bool] = None
    paid_by_user_id: Optional[str] = None
    activity_id: Optional[str] = None
    diary_entry_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validaciones básicas del DTO"""
        if self.amount is not None and self.amount <= 0:
            raise ValueError("amount debe ser mayor a cero")
        
        if self.currency is not None:
            if not self.currency or len(self.currency) != 3:
                raise ValueError("currency debe ser código ISO de 3 letras")
            self.currency = self.currency.upper()
        
        if self.description is not None:
            if len(self.description.strip()) < 3:
                raise ValueError("description debe tener al menos 3 caracteres")
            self.description = self.description.strip()
        
        if self.location is not None:
            self.location = self.location.strip()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UpdateExpenseDTO':
        """Crear DTO desde diccionario"""
        return cls(
            amount=Decimal(str(data["amount"])) if data.get("amount") is not None else None,
            currency=data.get("currency"),
            category=data.get("category"),
            description=data.get("description"),
            location=data.get("location"),
            is_shared=data.get("is_shared"),
            paid_by_user_id=data.get("paid_by_user_id"),
            activity_id=data.get("activity_id"),
            diary_entry_id=data.get("diary_entry_id"),
            metadata=data.get("metadata")
        )

    def has_updates(self) -> bool:
        """Verificar si el DTO tiene actualizaciones"""
        return any([
            self.amount is not None,
            self.currency is not None,
            self.category is not None,
            self.description is not None,
            self.location is not None,
            self.is_shared is not None,
            self.paid_by_user_id is not None,
            self.activity_id is not None,
            self.diary_entry_id is not None,
            self.metadata is not None
        ])