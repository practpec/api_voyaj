from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DifferenceMetric(Enum):
    """Métricas disponibles para diferencias plan vs realidad"""
    TIME_SPENT = "tiempo_invertido"
    COST_VARIATION = "variacion_costo"
    ACTIVITY_CHANGED = "actividad_cambio"
    LOCATION_CHANGED = "ubicacion_cambio"
    EXPERIENCE_RATING = "valoracion_experiencia"
    PARTICIPANT_COUNT = "numero_participantes"
    WEATHER_IMPACT = "impacto_clima"
    DURATION_CHANGE = "cambio_duracion"
    BUDGET_DEVIATION = "desviacion_presupuesto"
    OTHER = "otro"


@dataclass
class CreatePlanRealityDifferenceDTO:
    trip_id: str
    metric: str
    planned_value: str
    actual_value: str
    notes: Optional[str] = None
    day_id: Optional[str] = None
    activity_id: Optional[str] = None


@dataclass 
class UpdatePlanRealityDifferenceDTO:
    metric: Optional[str] = None
    planned_value: Optional[str] = None
    actual_value: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class PlanRealityDifferenceResponseDTO:
    id: str
    trip_id: str
    day_id: Optional[str]
    activity_id: Optional[str]
    metric: str
    metric_label: str
    planned_value: str
    actual_value: str
    notes: Optional[str]
    difference_detected: bool
    variance_percentage: Optional[float]
    impact_level: str
    created_at: datetime
    # Información adicional del contexto
    trip_title: Optional[str] = None
    day_date: Optional[str] = None
    activity_title: Optional[str] = None


@dataclass
class TripAnalysisResponseDTO:
    trip_id: str
    trip_title: str
    total_differences: int
    differences_by_metric: Dict[str, int]
    major_variances: List[PlanRealityDifferenceResponseDTO]
    budget_variance: float
    time_variance: float
    overall_satisfaction: Optional[float]
    recommendations: List[str]


@dataclass
class TripInsightsResponseDTO:
    trip_id: str
    insights: List[Dict[str, Any]]
    patterns_detected: List[str]
    improvement_suggestions: List[str]
    success_rate: float


class PlanRealityDifferenceDTOMapper:
    
    METRIC_LABELS = {
        DifferenceMetric.TIME_SPENT.value: "Tiempo Invertido",
        DifferenceMetric.COST_VARIATION.value: "Variación de Costo",
        DifferenceMetric.ACTIVITY_CHANGED.value: "Cambio de Actividad",
        DifferenceMetric.LOCATION_CHANGED.value: "Cambio de Ubicación",
        DifferenceMetric.EXPERIENCE_RATING.value: "Valoración de Experiencia",
        DifferenceMetric.PARTICIPANT_COUNT.value: "Número de Participantes",
        DifferenceMetric.WEATHER_IMPACT.value: "Impacto del Clima",
        DifferenceMetric.DURATION_CHANGE.value: "Cambio de Duración",
        DifferenceMetric.BUDGET_DEVIATION.value: "Desviación de Presupuesto",
        DifferenceMetric.OTHER.value: "Otro"
    }

    @staticmethod
    def to_response_dto(
        difference: Any,
        trip_title: Optional[str] = None,
        day_date: Optional[str] = None,
        activity_title: Optional[str] = None
    ) -> PlanRealityDifferenceResponseDTO:
        """Mapear diferencia a DTO de respuesta"""
        variance_percentage = PlanRealityDifferenceDTOMapper._calculate_variance_percentage(
            difference.planned_value, difference.actual_value
        )
        
        impact_level = PlanRealityDifferenceDTOMapper._determine_impact_level(
            difference.metric, variance_percentage
        )
        
        return PlanRealityDifferenceResponseDTO(
            id=difference.id,
            trip_id=difference.trip_id,
            day_id=difference.day_id,
            activity_id=difference.activity_id,
            metric=difference.metric,
            metric_label=PlanRealityDifferenceDTOMapper.METRIC_LABELS.get(
                difference.metric, difference.metric
            ),
            planned_value=difference.planned_value,
            actual_value=difference.actual_value,
            notes=difference.notes,
            difference_detected=difference.planned_value != difference.actual_value,
            variance_percentage=variance_percentage,
            impact_level=impact_level,
            created_at=difference.created_at,
            trip_title=trip_title,
            day_date=day_date,
            activity_title=activity_title
        )

    @staticmethod
    def _calculate_variance_percentage(planned_value: str, actual_value: str) -> Optional[float]:
        """Calcular porcentaje de variación para valores numéricos"""
        try:
            planned_num = float(planned_value)
            actual_num = float(actual_value)
            
            if planned_num == 0:
                return 100.0 if actual_num != 0 else 0.0
            
            return ((actual_num - planned_num) / planned_num) * 100
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _determine_impact_level(metric: str, variance_percentage: Optional[float]) -> str:
        """Determinar nivel de impacto basado en la métrica y variación"""
        if variance_percentage is None:
            return "neutral"
        
        abs_variance = abs(variance_percentage)
        
        # Criterios específicos por métrica
        if metric in [DifferenceMetric.COST_VARIATION.value, DifferenceMetric.BUDGET_DEVIATION.value]:
            if abs_variance >= 50:
                return "alto"
            elif abs_variance >= 20:
                return "medio"
            else:
                return "bajo"
        
        elif metric in [DifferenceMetric.TIME_SPENT.value, DifferenceMetric.DURATION_CHANGE.value]:
            if abs_variance >= 100:
                return "alto"
            elif abs_variance >= 50:
                return "medio"
            else:
                return "bajo"
        
        # Criterio general
        if abs_variance >= 30:
            return "alto"
        elif abs_variance >= 15:
            return "medio"
        else:
            return "bajo"