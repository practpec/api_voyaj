from typing import Dict, Any
from ...domain.expense_events import (
    ExpenseCreatedEvent,
    ExpenseUpdatedEvent,
    ExpenseDeletedEvent,
    ExpenseConfirmedEvent,
    ExpenseReceiptUploadedEvent,
    ExpenseBudgetExceededEvent,
    ExpenseSharedEvent
)
from shared.events.base_event import BaseEventHandler


class ExpenseNotificationHandler(BaseEventHandler):
    """Manejador de eventos para notificaciones de gastos"""

    async def handle_expense_created(self, event: ExpenseCreatedEvent) -> None:
        """Manejar evento de gasto creado"""
        # Notificar a miembros del viaje sobre nuevo gasto
        await self._send_notification({
            "type": "expense_created",
            "trip_id": event.trip_id,
            "expense_id": event.expense_id,
            "user_id": event.user_id,
            "amount": float(event.amount),
            "currency": event.currency,
            "category": event.category,
            "is_shared": event.is_shared,
            "message": f"Nuevo gasto registrado: {event.currency} {event.amount}"
        })

    async def handle_expense_updated(self, event: ExpenseUpdatedEvent) -> None:
        """Manejar evento de gasto actualizado"""
        # Solo notificar cambios significativos
        significant_changes = ["amount", "category", "is_shared"]
        if any(field in event.updated_fields for field in significant_changes):
            await self._send_notification({
                "type": "expense_updated",
                "trip_id": event.trip_id,
                "expense_id": event.expense_id,
                "user_id": event.user_id,
                "updated_fields": list(event.updated_fields.keys()),
                "message": "Gasto actualizado con cambios importantes"
            })

    async def handle_expense_deleted(self, event: ExpenseDeletedEvent) -> None:
        """Manejar evento de gasto eliminado"""
        await self._send_notification({
            "type": "expense_deleted",
            "trip_id": event.trip_id,
            "expense_id": event.expense_id,
            "user_id": event.user_id,
            "amount": float(event.amount),
            "currency": event.currency,
            "message": f"Gasto eliminado: {event.currency} {event.amount}"
        })

    async def handle_expense_confirmed(self, event: ExpenseConfirmedEvent) -> None:
        """Manejar evento de gasto confirmado"""
        if event.is_shared:
            await self._send_notification({
                "type": "expense_confirmed",
                "trip_id": event.trip_id,
                "expense_id": event.expense_id,
                "user_id": event.user_id,
                "amount": float(event.amount),
                "currency": event.currency,
                "message": f"Gasto compartido confirmado y listo para dividir"
            })

    async def handle_expense_receipt_uploaded(self, event: ExpenseReceiptUploadedEvent) -> None:
        """Manejar evento de comprobante subido"""
        await self._send_notification({
            "type": "expense_receipt_uploaded",
            "trip_id": event.trip_id,
            "expense_id": event.expense_id,
            "user_id": event.user_id,
            "receipt_url": event.receipt_url,
            "message": "Comprobante subido para gasto"
        })

    async def handle_expense_budget_exceeded(self, event: ExpenseBudgetExceededEvent) -> None:
        """Manejar evento de presupuesto excedido"""
        await self._send_notification({
            "type": "expense_budget_exceeded",
            "trip_id": event.trip_id,
            "total_expenses": float(event.total_expenses),
            "budget_limit": float(event.budget_limit),
            "exceeded_by": float(event.exceeded_by),
            "currency": event.currency,
            "message": f"⚠️ Presupuesto excedido por {event.currency} {event.exceeded_by}",
            "priority": "high"
        })

    async def handle_expense_shared(self, event: ExpenseSharedEvent) -> None:
        """Manejar evento de gasto compartido"""
        await self._send_notification({
            "type": "expense_shared",
            "trip_id": event.trip_id,
            "expense_id": event.expense_id,
            "user_id": event.user_id,
            "amount": float(event.amount),
            "currency": event.currency,
            "message": f"Gasto marcado como compartido: {event.currency} {event.amount}"
        })

    async def _send_notification(self, notification_data: Dict[str, Any]) -> None:
        """Enviar notificación a usuarios relevantes"""
        try:
            # Aquí se implementaría la lógica real de notificaciones
            # Por ejemplo: push notifications, emails, notificaciones in-app
            print(f"[EXPENSE NOTIFICATION] {notification_data}")
            
            # En una implementación real:
            # 1. Obtener miembros del viaje
            # 2. Determinar quién debe recibir la notificación
            # 3. Enviar notificación por los canales apropiados
            # 4. Guardar notificación en base de datos
            
        except Exception as e:
            print(f"[ERROR] Error enviando notificación de gasto: {str(e)}")