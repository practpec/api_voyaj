# src/modules/activities/application/dtos/activity_dto.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any


@dataclass
class CreateActivityDTO:
    day_id: str
    title: str
    description: Optional[str] = None
    category: str = "general"
    estimated_duration: Optional[int] = None
    estimated_cost: Optional[float] = None
    currency: str = "USD"
    location: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None
    notes: Optional[str] = None
    priority: str = "medium"
    tags: Optional[List[str]] = None
    external_links: Optional[List[str]] = None
    booking_info: Optional[Dict[str, Any]] = None


@dataclass
class UpdateActivityDTO:
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    estimated_duration: Optional[int] = None
    estimated_cost: Optional[float] = None
    currency: Optional[str] = None
    location: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None
    notes: Optional[str] = None
    priority: Optional[str] = None
    tags: Optional[List[str]] = None
    external_links: Optional[List[str]] = None
    booking_info: Optional[Dict[str, Any]] = None
    actual_duration: Optional[int] = None
    actual_cost: Optional[float] = None
    rating: Optional[int] = None
    review: Optional[str] = None


@dataclass
class ChangeActivityStatusDTO:
    status: str
    notes: Optional[str] = None
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    actual_cost: Optional[float] = None


@dataclass
class ReorderActivitiesDTO:
    activity_orders: List[Dict[str, Any]]


@dataclass
class ActivityResponseDTO:
    id: str
    day_id: str
    trip_id: str
    title: str
    description: Optional[str]
    category: str
    status: str
    priority: str
    order: int
    estimated_duration: Optional[int]
    actual_duration: Optional[int]
    estimated_cost: Optional[float]
    actual_cost: Optional[float]
    currency: str
    location: Optional[str]
    coordinates: Optional[Dict[str, float]]
    notes: Optional[str]
    tags: List[str]
    external_links: List[str]
    booking_info: Optional[Dict[str, Any]]
    rating: Optional[int]
    review: Optional[str]
    created_by: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]


@dataclass
class DayActivitiesResponseDTO:
    day_id: str
    trip_id: str
    activities: List[ActivityResponseDTO]
    stats: Optional[Dict[str, Any]] = None


@dataclass
class ActivitySummaryDTO:
    total_activities: int
    completed_activities: int
    pending_activities: int
    cancelled_activities: int
    total_estimated_cost: float
    total_actual_cost: float
    total_estimated_duration: int
    total_actual_duration: int
    activities_by_category: Dict[str, int]
    activities_by_priority: Dict[str, int]


class ActivityDTOMapper:
    
    @staticmethod
    def to_activity_response(activity_data: Dict[str, Any]) -> ActivityResponseDTO:
        return ActivityResponseDTO(
            id=activity_data.get("id"),
            day_id=activity_data.get("day_id"),
            trip_id=activity_data.get("trip_id"),
            title=activity_data.get("title"),
            description=activity_data.get("description"),
            category=activity_data.get("category"),
            status=activity_data.get("status"),
            priority=activity_data.get("priority"),
            order=activity_data.get("order", 0),
            estimated_duration=activity_data.get("estimated_duration"),
            actual_duration=activity_data.get("actual_duration"),
            estimated_cost=activity_data.get("estimated_cost"),
            actual_cost=activity_data.get("actual_cost"),
            currency=activity_data.get("currency", "USD"),
            location=activity_data.get("location"),
            coordinates=activity_data.get("coordinates"),
            notes=activity_data.get("notes"),
            tags=activity_data.get("tags", []),
            external_links=activity_data.get("external_links", []),
            booking_info=activity_data.get("booking_info"),
            rating=activity_data.get("rating"),
            review=activity_data.get("review"),
            created_by=activity_data.get("created_by"),
            created_at=activity_data.get("created_at"),
            updated_at=activity_data.get("updated_at"),
            completed_at=activity_data.get("completed_at")
        )

    @staticmethod
    def to_day_activities_response(
        day_id: str, 
        trip_id: str, 
        activities: List[Dict[str, Any]], 
        stats: Optional[Dict[str, Any]] = None
    ) -> DayActivitiesResponseDTO:
        activity_responses = [
            ActivityDTOMapper.to_activity_response(activity) 
            for activity in activities
        ]
        
        return DayActivitiesResponseDTO(
            day_id=day_id,
            trip_id=trip_id,
            activities=activity_responses,
            stats=stats
        )