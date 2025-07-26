from typing import List, Dict, Any, Optional
from datetime import datetime

from .interfaces.IPlanRealityDifferenceRepository import IPlanRealityDifferenceRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository


class PlanRealityDifferenceService:
    """Servicio de dominio para gestión de diferencias plan vs realidad"""
    
    def __init__(
        self,
        plan_reality_difference_repository: IPlanRealityDifferenceRepository,
        trip_member_repository: ITripMemberRepository
    ):
        self._plan_reality_difference_repository = plan_reality_difference_repository
        self._trip_member_repository = trip_member_repository

    async def validate_trip_access(self, trip_id: str, user_id: str) -> bool:
        """Validar que el usuario tenga acceso al viaje"""
        try:
            member = await self._trip_member_repository.find_by_trip_and_user(trip_id, user_id)
            return member is not None
        except:
            return False

    async def get_trip_analysis(self, trip_id: str) -> Dict[str, Any]:
        """Obtener análisis completo de diferencias del viaje"""
        differences = await self._plan_reality_difference_repository.find_by_trip_id(trip_id)
        
        total_differences = len(differences)
        
        # Agrupar por métrica
        differences_by_metric = {}
        major_variances = []
        
        for diff in differences:
            metric = diff.metric
            if metric not in differences_by_metric:
                differences_by_metric[metric] = 0
            differences_by_metric[metric] += 1
            
            # Identificar variaciones importantes
            variance = diff.get_variance_percentage()
            if variance and abs(variance) >= 30:  # Variación mayor al 30%
                major_variances.append(diff)
        
        # Calcular variaciones promedio de presupuesto y tiempo
        budget_variance = await self._calculate_budget_variance(differences)
        time_variance = await self._calculate_time_variance(differences)
        
        return {
            "total_differences": total_differences,
            "differences_by_metric": differences_by_metric,
            "major_variances": major_variances,
            "budget_variance": budget_variance,
            "time_variance": time_variance,
            "overall_satisfaction": await self._calculate_satisfaction_score(differences),
            "recommendations": await self._generate_recommendations(differences)
        }

    async def get_trip_insights(self, trip_id: str) -> Dict[str, Any]:
        """Generar insights del viaje basados en diferencias"""
        differences = await self._plan_reality_difference_repository.find_by_trip_id(trip_id)
        
        insights = []
        patterns_detected = []
        improvement_suggestions = []
        
        # Analizar patrones
        cost_variations = [d for d in differences if d.metric in ["variacion_costo", "desviacion_presupuesto"]]
        time_variations = [d for d in differences if d.metric in ["tiempo_invertido", "cambio_duracion"]]
        
        if cost_variations:
            avg_cost_variance = sum(
                d.get_variance_percentage() or 0 for d in cost_variations
            ) / len(cost_variations)
            
            insights.append({
                "type": "cost_analysis",
                "title": "Análisis de Costos",
                "description": f"Variación promedio de costos: {avg_cost_variance:.1f}%",
                "variance": avg_cost_variance
            })
            
            if avg_cost_variance > 20:
                patterns_detected.append("Tendencia a exceder presupuesto planificado")
                improvement_suggestions.append("Considerar un margen de seguridad del 25% en costos")
        
        if time_variations:
            avg_time_variance = sum(
                d.get_variance_percentage() or 0 for d in time_variations
            ) / len(time_variations)
            
            insights.append({
                "type": "time_analysis",
                "title": "Análisis de Tiempo",
                "description": f"Variación promedio de tiempo: {avg_time_variance:.1f}%",
                "variance": avg_time_variance
            })
            
            if avg_time_variance > 50:
                patterns_detected.append("Actividades tienden a tomar más tiempo del planificado")
                improvement_suggestions.append("Agregar tiempo adicional entre actividades")
        
        # Calcular tasa de éxito
        success_rate = await self._calculate_success_rate(differences)
        
        return {
            "insights": insights,
            "patterns_detected": patterns_detected,
            "improvement_suggestions": improvement_suggestions,
            "success_rate": success_rate
        }

    async def _calculate_budget_variance(self, differences: List[Any]) -> float:
        """Calcular variación promedio de presupuesto"""
        budget_diffs = [
            d for d in differences 
            if d.metric in ["variacion_costo", "desviacion_presupuesto"]
        ]
        
        if not budget_diffs:
            return 0.0
        
        variances = [d.get_variance_percentage() for d in budget_diffs if d.get_variance_percentage() is not None]
        
        if not variances:
            return 0.0
        
        return sum(variances) / len(variances)

    async def _calculate_time_variance(self, differences: List[Any]) -> float:
        """Calcular variación promedio de tiempo"""
        time_diffs = [
            d for d in differences 
            if d.metric in ["tiempo_invertido", "cambio_duracion"]
        ]
        
        if not time_diffs:
            return 0.0
        
        variances = [d.get_variance_percentage() for d in time_diffs if d.get_variance_percentage() is not None]
        
        if not variances:
            return 0.0
        
        return sum(variances) / len(variances)

    async def _calculate_satisfaction_score(self, differences: List[Any]) -> Optional[float]:
        """Calcular puntuación de satisfacción basada en valoraciones"""
        satisfaction_diffs = [
            d for d in differences 
            if d.metric == "valoracion_experiencia"
        ]
        
        if not satisfaction_diffs:
            return None
        
        try:
            ratings = [float(d.actual_value) for d in satisfaction_diffs]
            return sum(ratings) / len(ratings)
        except (ValueError, TypeError):
            return None

    async def _generate_recommendations(self, differences: List[Any]) -> List[str]:
        """Generar recomendaciones basadas en las diferencias"""
        recommendations = []
        
        # Analizar patrones comunes
        cost_overruns = len([d for d in differences if d.metric in ["variacion_costo"] and d.get_variance_percentage() and d.get_variance_percentage() > 20])
        time_overruns = len([d for d in differences if d.metric in ["tiempo_invertido"] and d.get_variance_percentage() and d.get_variance_percentage() > 50])
        
        if cost_overruns > 2:
            recommendations.append("Establecer presupuestos más realistas con margen de seguridad")
        
        if time_overruns > 2:
            recommendations.append("Planificar horarios con mayor flexibilidad")
        
        # Recomendaciones adicionales basadas en actividades cambiadas
        activity_changes = len([d for d in differences if d.metric == "actividad_cambio"])
        if activity_changes > 3:
            recommendations.append("Investigar mejor las actividades antes del viaje")
        
        if not recommendations:
            recommendations.append("El viaje se ejecutó según el plan, ¡excelente planificación!")
        
        return recommendations

    async def _calculate_success_rate(self, differences: List[Any]) -> float:
        """Calcular tasa de éxito del viaje"""
        if not differences:
            return 100.0
        
        # Contar diferencias significativas (variación > 25%)
        significant_differences = 0
        total_measurable = 0
        
        for diff in differences:
            variance = diff.get_variance_percentage()
            if variance is not None:
                total_measurable += 1
                if abs(variance) > 25:
                    significant_differences += 1
        
        if total_measurable == 0:
            return 100.0
        
        success_rate = ((total_measurable - significant_differences) / total_measurable) * 100
        return max(0.0, success_rate)