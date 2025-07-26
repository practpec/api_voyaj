from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
from ...domain.trip import TripData, TripCategory, TripStatus


@dataclass
class CreateTripDTO:
    title: str
    description: Optional[str]
    destination: str
    start_date: datetime
    end_date: datetime
    category: TripCategory = TripCategory.LEISURE
    is_group_trip: bool = False
    is_public: bool = False
    budget_limit: Optional[float] = None
    currency: str = "USD"
    image_url: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class UpdateTripDTO:
    title: Optional[str] = None
    description: Optional[str] = None
    destination: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    category: Optional[TripCategory] = None
    budget_limit: Optional[float] = None
    is_public: Optional[bool] = None
    image_url: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class UpdateTripStatusDTO:
    status: TripStatus


@dataclass
class TripFiltersDTO:
    status: Optional[str] = None
    category: Optional[str] = None
    is_group_trip: Optional[bool] = None
    destination: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = True
    limit: int = 20
    offset: int = 0


@dataclass
class TripResponseDTO:
    id: str
    title: str
    description: Optional[str]
    destination: str
    start_date: datetime
    end_date: datetime
    owner_id: str
    category: str
    status: str
    is_group_trip: bool
    is_public: bool
    budget_limit: Optional[float]
    currency: str
    image_url: Optional[str]
    notes: Optional[str]
    total_expenses: float
    member_count: int
    created_at: datetime
    updated_at: datetime
    owner_info: Optional[Dict[str, Any]] = None
    user_role: Optional[str] = None
    can_edit: bool = False


@dataclass
class TripListResponseDTO:
    id: str
    title: str
    destination: str
    start_date: datetime
    end_date: datetime
    status: str
    category: str
    is_group_trip: bool
    member_count: int
    total_expenses: float
    image_url: Optional[str]
    user_role: Optional[str] = None


@dataclass
class TripStatsDTO:
    total_trips: int
    completed_trips: int
    active_trips: int
    total_expenses: float
    average_trip_duration: float
    most_visited_destination: Optional[str] = None
    favorite_category: Optional[str] = None


class TripDTOMapper:
    
    @staticmethod
    def to_trip_response(
        trip: TripData,
        owner_info: Optional[Dict[str, Any]] = None,
        user_role: Optional[str] = None,
        can_edit: bool = False
    ) -> TripResponseDTO:
        return TripResponseDTO(
            id=trip.id,
            title=trip.title,
            description=trip.description,
            destination=trip.destination,
            start_date=trip.start_date,
            end_date=trip.end_date,
            owner_id=trip.owner_id,
            category=trip.category,
            status=trip.status,
            is_group_trip=trip.is_group_trip,
            is_public=trip.is_public,
            budget_limit=trip.budget_limit,
            currency=trip.currency,
            image_url=trip.image_url,
            notes=trip.notes,
            total_expenses=trip.total_expenses,
            member_count=trip.member_count,
            created_at=trip.created_at,
            updated_at=trip.updated_at,
            owner_info=owner_info,
            user_role=user_role,
            can_edit=can_edit
        )

    @staticmethod
    def to_trip_list_response(
        trip: TripData,
        user_role: Optional[str] = None
    ) -> TripListResponseDTO:
        return TripListResponseDTO(
            id=trip.id,
            title=trip.title,
            destination=trip.destination,
            start_date=trip.start_date,
            end_date=trip.end_date,
            status=trip.status,
            category=trip.category,
            is_group_trip=trip.is_group_trip,
            member_count=trip.member_count,
            total_expenses=trip.total_expenses,
            image_url=trip.image_url,
            user_role=user_role
        )

    @staticmethod
    def to_trip_stats(stats_data: Dict[str, Any]) -> TripStatsDTO:
        return TripStatsDTO(
            total_trips=stats_data.get("total_trips", 0),
            completed_trips=stats_data.get("completed_trips", 0),
            active_trips=stats_data.get("active_trips", 0),
            total_expenses=stats_data.get("total_expenses", 0.0),
            average_trip_duration=stats_data.get("average_trip_duration", 0.0),
            most_visited_destination=stats_data.get("most_visited_destination"),
            favorite_category=stats_data.get("favorite_category")
        )