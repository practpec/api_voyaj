from typing import Dict, Any, Optional
from decimal import Decimal
from datetime import datetime
from ...domain.expense_service import ExpenseService
from ...domain.expense_events import ExpenseBudgetExceededEvent
from shared.events.event_bus import EventBus


class BudgetTrackingService:
    """Servicio para monitoreo de presupuesto"""

    def __init__(self, expense_service: ExpenseService, event_bus: EventBus):
        self._expense_service = expense_service
        self._event_bus = event_bus

    async def check_budget_status(self, trip_id: str, budget_limit: Decimal, currency: str) -> Dict[str, Any]:
        """Verificar estado del presupuesto del viaje"""
        
        # Obtener total de gastos
        total_summary = await self._expense_service.calculate_trip_total(trip_id, currency)
        total_expenses = total_summary["overall_total"]

        # Calcular porcentaje usado
        percentage_used = (total_expenses / budget_limit * 100) if budget_limit > 0 else 0
        remaining_budget = budget_limit - total_expenses
        is_exceeded = total_expenses > budget_limit

        # Determinar nivel de alerta
        alert_level = self._get_alert_level(percentage_used, is_exceeded)

        # Si se excede el presupuesto, publicar evento
        if is_exceeded:
            exceeded_by = total_expenses - budget_limit
            event = ExpenseBudgetExceededEvent(
                trip_id=trip_id,
                total_expenses=total_expenses,
                budget_limit=budget_limit,
                currency=currency,
                exceeded_by=exceeded_by
            )
            await self._event_bus.publish(event)

        return {
            "trip_id": trip_id,
            "budget_limit": float(budget_limit),
            "total_expenses": float(total_expenses),
            "remaining_budget": float(remaining_budget),
            "percentage_used": float(percentage_used),
            "is_exceeded": is_exceeded,
            "alert_level": alert_level,
            "currency": currency,
            "status": self._get_budget_status(percentage_used, is_exceeded),
            "checked_at": datetime.utcnow().isoformat()
        }

    async def get_budget_recommendations(self, trip_id: str, budget_limit: Decimal, currency: str) -> Dict[str, Any]:
        """Obtener recomendaciones basadas en gastos actuales"""
        
        budget_status = await self.check_budget_status(trip_id, budget_limit, currency)
        categories_summary = await self._expense_service.get_expenses_by_category(trip_id)
        daily_average = await self._expense_service.calculate_average_daily_spending(trip_id)

        recommendations = []

        # Recomendaciones basadas en estado del presupuesto
        if budget_status["is_exceeded"]:
            recommendations.append({
                "type": "budget_exceeded",
                "priority": "high",
                "message": "Has excedido tu presupuesto. Considera revisar gastos no esenciales.",
                "action": "review_expenses"
            })
        elif budget_status["percentage_used"] > 80:
            recommendations.append({
                "type": "budget_warning",
                "priority": "medium",
                "message": "Estás cerca del límite del presupuesto. Planifica cuidadosamente los gastos restantes.",
                "action": "plan_remaining_expenses"
            })

        # Recomendaciones basadas en categorías
        if categories_summary:
            max_category = max(categories_summary.items(), key=lambda x: x[1])
            if max_category[1] > budget_limit * Decimal("0.4"):  # Más del 40% en una categoría
                recommendations.append({
                    "type": "category_concentration",
                    "priority": "medium",
                    "message": f"Gran parte del presupuesto se concentra en {max_category[0].value}. Considera diversificar gastos.",
                    "category": max_category[0].value,
                    "amount": float(max_category[1])
                })

        # Recomendaciones basadas en promedio diario
        if daily_average["average_daily"] > 0:
            daily_limit = budget_limit / 30  # Asumiendo 30 días promedio
            if daily_average["average_daily"] > daily_limit:
                recommendations.append({
                    "type": "daily_spending_high",
                    "priority": "medium",
                    "message": f"Tu promedio diario ({currency} {daily_average['average_daily']}) está por encima del límite recomendado.",
                    "daily_average": float(daily_average["average_daily"]),
                    "recommended_daily": float(daily_limit)
                })

        return {
            "budget_status": budget_status,
            "recommendations": recommendations,
            "daily_spending": daily_average,
            "category_breakdown": {k.value: float(v) for k, v in categories_summary.items()}
        }

    async def project_budget_usage(self, trip_id: str, days_remaining: int) -> Dict[str, Any]:
        """Proyectar uso de presupuesto basado en tendencias actuales"""
        
        daily_average = await self._expense_service.calculate_average_daily_spending(trip_id, days=14)  # Últimas 2 semanas
        
        if daily_average["average_daily"] <= 0:
            return {
                "projection_available": False,
                "message": "No hay suficientes datos para proyectar gastos"
            }

        projected_expenses = daily_average["average_daily"] * days_remaining
        
        return {
            "projection_available": True,
            "days_remaining": days_remaining,
            "current_daily_average": float(daily_average["average_daily"]),
            "projected_expenses": float(projected_expenses),
            "based_on_days": daily_average["total_days"],
            "confidence_level": self._calculate_confidence_level(daily_average["total_days"]),
            "projection_date": datetime.utcnow().isoformat()
        }

    def _get_alert_level(self, percentage_used: float, is_exceeded: bool) -> str:
        """Determinar nivel de alerta basado en uso del presupuesto"""
        if is_exceeded:
            return "critical"
        elif percentage_used >= 90:
            return "high"
        elif percentage_used >= 75:
            return "medium"
        elif percentage_used >= 50:
            return "low"
        else:
            return "none"

    def _get_budget_status(self, percentage_used: float, is_exceeded: bool) -> str:
        """Obtener estado descriptivo del presupuesto"""
        if is_exceeded:
            return "exceeded"
        elif percentage_used >= 90:
            return "critical"
        elif percentage_used >= 75:
            return "warning"
        elif percentage_used >= 50:
            return "caution"
        else:
            return "healthy"

    def _calculate_confidence_level(self, days_with_data: int) -> str:
        """Calcular nivel de confianza de la proyección"""
        if days_with_data >= 14:
            return "high"
        elif days_with_data >= 7:
            return "medium"
        elif days_with_data >= 3:
            return "low"
        else:
            return "very_low"