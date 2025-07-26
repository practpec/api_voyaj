from dataclasses import dataclass
from datetime import datetime, time
from typing import Optional, List, Dict, Any
from ...domain.activity import ActivityData, ActivityCategory, ActivityStatus


@dataclass
class CreateActivityDTO:
    day_id: str
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    estimated_cost: Optional[float] = None
    category: ActivityCategory = ActivityCategory.OTHER


@dataclass
class UpdateActivityDTO:
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    estimated_cost: Optional[float] = None
    category: Optional[ActivityCategory] = None


@dataclass
class ChangeActivityStatusDTO:
    status: ActivityStatus
    actual_cost: Optional[float] = None


@dataclass
class ReorderActivitiesDTO:
    day_id: str
    activity_orders: List[Dict[str, Any]]  # [{"activity_id": str, "order": int}]


@dataclass
class ActivityFiltersDTO:
    day_id: Optional[str] = None
    trip_id: Optional[str] = None
    status: Optional[str] = None
    category: Optional[str] = None
    created_by: Optional[str] = None
    has_cost: Optional[bool] = None
    limit: int = 50
    offset: int = 0


@dataclass
class ActivityResponseDTO:
    id: str
    day_id: str
    title: str
    description: Optional[str]
    location: Optional[str]
    start_time: Optional[time]
    end_time: Optional[time]
    estimated_cost: Optional[float]
    actual_cost: Optional[float]
    category: str
    status: str
    order: int
    duration_minutes: Optional[int]
    created_by: str
    created_at: datetime
    updated_at: datetime
    can_edit: bool = False
    can_change_status: bool = False
    creator_info: Optional[Dict[str, Any]] = None


@dataclass
class ActivityListResponseDTO:
    id: str
    title: str
    location: Optional[str]
    start_time: Optional[time]
    end_time: Optional[time]
    estimated_cost: Optional[float]
    category: str
    status: str
    order: int
    duration_minutes: Optional[int]


@dataclass
class DayActivitiesResponseDTO:
    day_id: str
    day_date: str
    activities: List[ActivityListResponseDTO]
    total_activities: int
    completed_activities: int
    total_estimated_cost: float
    total_actual_cost: float
    completion_percentage: float


@dataclass
class ActivityStatsDTO:
    total_activities: int
    completed_activities: int
    in_progress_activities: int
    planned_activities: int
    cancelled_activities: int
    completion_percentage: float
    total_estimated_cost: float
    total_actual_cost: float
    activities_by_category: Dict[str, int]


@dataclass
class ReorderResponseDTO:
    reordered_activities: List[ActivityListResponseDTO]
    total_reordered: int
    message: str


class ActivityDTOMapper:
    
    CATEGORY_LABELS = {
        ActivityCategory.TRANSPORT.value: "Transporte",
        ActivityCategory.ACCOMMODATION.value: "Alojamiento", 
        ActivityCategory.FOOD.value: "Comida",
        ActivityCategory.SIGHTSEEING.value: "Turismo",
        ActivityCategory.ENTERTAINMENT.value: "Entretenimiento",
        ActivityCategory.SHOPPING.value: "Compras",
        ActivityCategory.ADVENTURE.value: "Aventura",
        ActivityCategory.RELAXATION.value: "Relajación",
        ActivityCategory.CULTURAL.value: "Cultural",
        ActivityCategory.BUSINESS.value: "Negocios",
        ActivityCategory.OTHER.value: "Otro"
    }
    
    STATUS_LABELS = {
        ActivityStatus.PLANNED.value: "Planificada",
        ActivityStatus.IN_PROGRESS.value: "En Progreso",
        ActivityStatus.COMPLETED.value: "Completada",
        ActivityStatus.CANCELLED.value: "Cancelada"
    }

    @staticmethod
    def to_activity_response(
        activity: ActivityData,
        can_edit: bool = False,
        can_change_status: bool = False,
        creator_info: Optional[Dict[str, Any]] = None
    ) -> ActivityResponseDTO:
        # Calcular duración si hay horas de inicio y fin
        duration_minutes = None
        if activity.start_time and activity.end_time:
            start_minutes = activity.start_time.hour * 60 + activity.start_time.minute
            end_minutes = activity.end_time.hour * 60 + activity.end_time.minute
            if end_minutes > start_minutes:
                duration_minutes = end_minutes - start_minutes

        return ActivityResponseDTO(
            id=activity.id,
            day_id=activity.day_id,
            title=activity.title,
            description=activity.description,
            location=activity.location,
            start_time=activity.start_time,
            end_time=activity.end_time,
            estimated_cost=activity.estimated_cost,
            actual_cost=activity.actual_cost,
            category=activity.category,
            status=activity.status,
            order=activity.order,
            duration_minutes=duration_minutes,
            created_by=activity.created_by,
            created_at=activity.created_at,
            updated_at=activity.updated_at,
            can_edit=can_edit,
            can_change_status=can_change_status,
            creator_info=creator_info
        )

    @staticmethod
    def to_activity_list_response(activity: ActivityData) -> ActivityListResponseDTO:
        # Calcular duración
        duration_minutes = None
        if activity.start_time and activity.end_time:
            start_minutes = activity.start_time.hour * 60 + activity.start_time.minute
            end_minutes = activity.end_time.hour * 60 + activity.end_time.minute
            if end_minutes > start_minutes:
                duration_minutes = end_minutes - start_minutes

        return ActivityListResponseDTO(
            id=activity.id,
            title=activity.title,
            location=activity.location,
            start_time=activity.start_time,
            end_time=activity.end_time,
            estimated_cost=activity.estimated_cost,
            category=activity.category,
            status=activity.status,
            order=activity.order,
            duration_minutes=duration_minutes
        )

    @staticmethod
    def to_day_activities_response(
        day_id: str,
        day_date: str,
        activities: List[ActivityListResponseDTO],
        stats: Dict[str, Any]
    ) -> DayActivitiesResponseDTO:
        return DayActivitiesResponseDTO(
            day_id=day_id,
            day_date=day_date,
            activities=activities,
            total_activities=stats.get("total_activities", 0),
            completed_activities=stats.get("completed_activities", 0),
            total_estimated_cost=stats.get("total_estimated_cost", 0.0),
            total_actual_cost=stats.get("total_actual_cost", 0.0),
            completion_percentage=stats.get("completion_percentage", 0.0)
        )

    @staticmethod
    def to_activity_stats(stats_data: Dict[str, Any]) -> ActivityStatsDTO:
        return ActivityStatsDTO(
            total_activities=stats_data.get("total_activities", 0),
            completed_activities=stats_data.get("completed_activities", 0),
            in_progress_activities=stats_data.get("in_progress_activities", 0),
            planned_activities=stats_data.get("planned_activities", 0),
            cancelled_activities=stats_data.get("cancelled_activities", 0),
            completion_percentage=stats_data.get("completion_percentage", 0.0),
            total_estimated_cost=stats_data.get("total_estimated_cost", 0.0),
            total_actual_cost=stats_data.get("total_actual_cost", 0.0),
            activities_by_category=stats_data.get("activities_by_category", {})
        )

    @staticmethod
    def to_reorder_response(
        activities: List[ActivityListResponseDTO]
    ) -> ReorderResponseDTO:
        return ReorderResponseDTO(
            reordered_activities=activities,
            total_reordered=len(activities),
            message=f"Se reordenaron {len(activities)} actividades exitosamente"
        )