from typing import List, Dict, Any
from decimal import Decimal
from .expense_split import ExpenseSplit, ExpenseSplitData, ExpenseSplitStatus
from .interfaces.expense_split_repository_interface import ExpenseSplitRepositoryInterface
from shared.errors.custom_errors import ValidationError, NotFoundError, BusinessRuleError


class ExpenseSplitService:
    def __init__(
        self,
        expense_split_repository: ExpenseSplitRepositoryInterface
    ):
        self._expense_split_repository = expense_split_repository

    async def create_expense_splits(
        self, 
        expense_id: str, 
        splits_data: List[Dict[str, Any]]
    ) -> List[ExpenseSplit]:
        """Crear múltiples divisiones para un gasto"""
        if not splits_data:
            raise ValidationError("Debe especificar al menos una división")

        # Validar que la suma de montos sea coherente
        total_amount = sum(Decimal(str(split['amount'])) for split in splits_data)
        if total_amount <= 0:
            raise ValidationError("El monto total de las divisiones debe ser mayor a cero")

        # Validar usuarios únicos
        user_ids = [split['user_id'] for split in splits_data]
        if len(user_ids) != len(set(user_ids)):
            raise ValidationError("No se pueden crear divisiones duplicadas para el mismo usuario")

        # Crear divisiones
        expense_splits = []
        for split_data in splits_data:
            data = ExpenseSplitData(
                id=self._generate_id(),
                expense_id=expense_id,
                user_id=split_data['user_id'],
                amount=Decimal(str(split_data['amount'])),
                notes=split_data.get('notes')
            )
            expense_split = ExpenseSplit(data)
            created_split = await self._expense_split_repository.create(expense_split)
            expense_splits.append(created_split)

        return expense_splits

    async def update_expense_splits(
        self, 
        expense_id: str, 
        splits_data: List[Dict[str, Any]]
    ) -> List[ExpenseSplit]:
        """Actualizar divisiones de un gasto"""
        # Eliminar divisiones existentes
        await self._expense_split_repository.delete_by_expense_id(expense_id)
        
        # Crear nuevas divisiones
        return await self.create_expense_splits(expense_id, splits_data)

    async def mark_split_as_paid(
        self, 
        expense_split_id: str, 
        notes: str = None
    ) -> ExpenseSplit:
        """Marcar división como pagada"""
        expense_split = await self._expense_split_repository.find_by_id(expense_split_id)
        if not expense_split:
            raise NotFoundError("División de gasto no encontrada")

        if not expense_split.is_active():
            raise BusinessRuleError("No se puede modificar una división eliminada")

        if expense_split.is_paid():
            raise BusinessRuleError("La división ya está marcada como pagada")

        expense_split.mark_as_paid(notes)
        return await self._expense_split_repository.update(expense_split)

    async def cancel_split(self, expense_split_id: str) -> ExpenseSplit:
        """Cancelar división de gasto"""
        expense_split = await self._expense_split_repository.find_by_id(expense_split_id)
        if not expense_split:
            raise NotFoundError("División de gasto no encontrada")

        if not expense_split.is_active():
            raise BusinessRuleError("No se puede modificar una división eliminada")

        if expense_split.is_cancelled():
            raise BusinessRuleError("La división ya está cancelada")

        expense_split.cancel()
        return await self._expense_split_repository.update(expense_split)

    async def calculate_trip_balances(self, trip_id: str) -> Dict[str, Any]:
        """Calcular balances entre usuarios en un viaje"""
        balances_data = await self._expense_split_repository.get_trip_balances(trip_id)
        
        # Procesar balances
        user_balances = {}
        total_debts = Decimal('0')
        total_credits = Decimal('0')
        
        for balance in balances_data:
            user_id = balance['user_id']
            amount_owed = Decimal(str(balance.get('amount_owed', 0)))
            amount_paid = Decimal(str(balance.get('amount_paid', 0)))
            net_balance = amount_paid - amount_owed
            
            user_balances[user_id] = {
                'amount_owed': amount_owed,
                'amount_paid': amount_paid,
                'net_balance': net_balance,
                'status': 'creditor' if net_balance > 0 else 'debtor' if net_balance < 0 else 'settled'
            }
            
            if net_balance > 0:
                total_credits += net_balance
            elif net_balance < 0:
                total_debts += abs(net_balance)

        return {
            'user_balances': user_balances,
            'total_debts': total_debts,
            'total_credits': total_credits,
            'is_balanced': total_debts == total_credits
        }

    async def validate_split_access(
        self, 
        expense_split: ExpenseSplit, 
        user_id: str
    ) -> bool:
        """Validar si el usuario puede acceder a la división"""
        return expense_split.user_id == user_id

    def _generate_id(self) -> str:
        """Generar ID único"""
        import uuid
        return str(uuid.uuid4())