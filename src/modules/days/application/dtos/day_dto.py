from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from ...domain.Day import DayData


@dataclass
class CreateDayDTO:
    trip_id: str
    date: date
    notes: Optional[str] = None


@dataclass
class UpdateDayDTO:
    notes: Optional[str] = None


@dataclass
class GenerateTripDaysDTO:
    trip_id: str


@dataclass
class DayFiltersDTO:
    trip_id: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    has_notes: Optional[bool] = None
    limit: int = 50
    offset: int = 0


@dataclass
class DayResponseDTO:
    id: str
    trip_id: str
    date: date
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    can_edit: bool = False
    activity_count: int = 0
    photo_count: int = 0


@dataclass
class DayListResponseDTO:
    id: str
    date: date
    notes: Optional[str]
    activity_count: int = 0
    photo_count: int = 0
    has_content: bool = False


@dataclass
class TripTimelineResponseDTO:
    trip_id: str
    days: List[DayListResponseDTO]
    total_days: int
    days_with_content: int
    completion_percentage: float


@dataclass
class DayStatsDTO:
    total_days: int
    days_with_notes: int
    days_with_activities: int
    days_with_photos: int
    completion_percentage: float


@dataclass
class BulkCreateDaysResponseDTO:
    created_days: List[DayResponseDTO]
    total_created: int
    skipped_dates: List[date]
    message: str


class DayDTOMapper:
    
    @staticmethod
    def to_day_response(
        day: DayData,
        can_edit: bool = False,
        activity_count: int = 0,
        photo_count: int = 0
    ) -> DayResponseDTO:
        return DayResponseDTO(
            id=day.id,
            trip_id=day.trip_id,
            date=day.date,
            notes=day.notes,
            created_at=day.created_at,
            updated_at=day.updated_at,
            can_edit=can_edit,
            activity_count=activity_count,
            photo_count=photo_count
        )

    @staticmethod
    def to_day_list_response(
        day: DayData,
        activity_count: int = 0,
        photo_count: int = 0
    ) -> DayListResponseDTO:
        has_content = bool(day.notes or activity_count > 0 or photo_count > 0)
        
        return DayListResponseDTO(
            id=day.id,
            date=day.date,
            notes=day.notes,
            activity_count=activity_count,
            photo_count=photo_count,
            has_content=has_content
        )

    @staticmethod
    def to_timeline_response(
        trip_id: str,
        days: List[DayListResponseDTO],
        stats: Dict[str, Any]
    ) -> TripTimelineResponseDTO:
        return TripTimelineResponseDTO(
            trip_id=trip_id,
            days=days,
            total_days=stats.get("total_days", 0),
            days_with_content=stats.get("days_with_content", 0),
            completion_percentage=stats.get("completion_percentage", 0.0)
        )

    @staticmethod
    def to_day_stats(stats_data: Dict[str, Any]) -> DayStatsDTO:
        return DayStatsDTO(
            total_days=stats_data.get("total_days", 0),
            days_with_notes=stats_data.get("days_with_notes", 0),
            days_with_activities=stats_data.get("days_with_activities", 0),
            days_with_photos=stats_data.get("days_with_photos", 0),
            completion_percentage=stats_data.get("completion_percentage", 0.0)
        )

    @staticmethod
    def to_bulk_create_response(
        created_days: List[DayResponseDTO],
        skipped_dates: List[date]
    ) -> BulkCreateDaysResponseDTO:
        return BulkCreateDaysResponseDTO(
            created_days=created_days,
            total_created=len(created_days),
            skipped_dates=skipped_dates,
            message=f"Se crearon {len(created_days)} días exitosamente"
        )