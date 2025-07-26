from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from uuid import uuid4


class TripStatus(str, Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TripCategory(str, Enum):
    LEISURE = "leisure"
    BUSINESS = "business"
    ADVENTURE = "adventure"
    CULTURAL = "cultural"
    ROMANTIC = "romantic"
    FAMILY = "family"
    BACKPACKING = "backpacking"
    LUXURY = "luxury"
    BUDGET = "budget"
    ECO = "eco"


@dataclass
class TripData:
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
    is_deleted: bool = False


class Trip:
    def __init__(
        self,
        id: str,
        title: str,
        description: Optional[str],
        destination: str,
        start_date: datetime,
        end_date: datetime,
        owner_id: str,
        category: str,
        status: str,
        is_group_trip: bool,
        is_public: bool,
        budget_limit: Optional[float],
        currency: str,
        image_url: Optional[str],
        notes: Optional[str],
        total_expenses: float,
        member_count: int,
        created_at: datetime,
        updated_at: datetime,
        is_deleted: bool = False
    ):
        self._id = id
        self._title = title
        self._description = description
        self._destination = destination
        self._start_date = start_date
        self._end_date = end_date
        self._owner_id = owner_id
        self._category = category
        self._status = status
        self._is_group_trip = is_group_trip
        self._is_public = is_public
        self._budget_limit = budget_limit
        self._currency = currency
        self._image_url = image_url
        self._notes = notes
        self._total_expenses = total_expenses
        self._member_count = member_count
        self._created_at = created_at
        self._updated_at = updated_at
        self._is_deleted = is_deleted

    @classmethod
    def create(
        cls,
        title: str,
        description: Optional[str],
        destination: str,
        start_date: datetime,
        end_date: datetime,
        owner_id: str,
        category: TripCategory = TripCategory.LEISURE,
        is_group_trip: bool = False,
        is_public: bool = False,
        budget_limit: Optional[float] = None,
        currency: str = "USD",
        image_url: Optional[str] = None,
        notes: Optional[str] = None
    ) -> 'Trip':
        if start_date >= end_date:
            raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin")
        
        return cls(
            id=str(uuid4()),
            title=title,
            description=description,
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            owner_id=owner_id,
            category=category.value,
            status=TripStatus.PLANNING.value,
            is_group_trip=is_group_trip,
            is_public=is_public,
            budget_limit=budget_limit,
            currency=currency,
            image_url=image_url,
            notes=notes,
            total_expenses=0.0,
            member_count=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_deleted=False
        )

    @classmethod
    def from_data(cls, data: TripData) -> 'Trip':
        return cls(
            id=data.id,
            title=data.title,
            description=data.description,
            destination=data.destination,
            start_date=data.start_date,
            end_date=data.end_date,
            owner_id=data.owner_id,
            category=data.category,
            status=data.status,
            is_group_trip=data.is_group_trip,
            is_public=data.is_public,
            budget_limit=data.budget_limit,
            currency=data.currency,
            image_url=data.image_url,
            notes=data.notes,
            total_expenses=data.total_expenses,
            member_count=data.member_count,
            created_at=data.created_at,
            updated_at=data.updated_at,
            is_deleted=data.is_deleted
        )

    def update_details(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        destination: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        category: Optional[TripCategory] = None,
        budget_limit: Optional[float] = None,
        is_public: Optional[bool] = None,
        image_url: Optional[str] = None,
        notes: Optional[str] = None
    ):
        if title is not None:
            self._title = title
        if description is not None:
            self._description = description
        if destination is not None:
            self._destination = destination
        if start_date is not None:
            self._start_date = start_date
        if end_date is not None:
            self._end_date = end_date
        if category is not None:
            self._category = category.value
        if budget_limit is not None:
            self._budget_limit = budget_limit
        if is_public is not None:
            self._is_public = is_public
        if image_url is not None:
            self._image_url = image_url
        if notes is not None:
            self._notes = notes
        
        self._updated_at = datetime.utcnow()

    def change_status(self, new_status: TripStatus):
        self._status = new_status.value
        self._updated_at = datetime.utcnow()

    def complete_trip(self):
        self._status = TripStatus.COMPLETED.value
        self._updated_at = datetime.utcnow()

    def cancel_trip(self):
        self._status = TripStatus.CANCELLED.value
        self._updated_at = datetime.utcnow()

    def update_expenses(self, total_expenses: float):
        self._total_expenses = total_expenses
        self._updated_at = datetime.utcnow()

    def update_member_count(self, count: int):
        self._member_count = count
        self._updated_at = datetime.utcnow()

    def soft_delete(self):
        self._is_deleted = True
        self._updated_at = datetime.utcnow()

    def restore(self):
        self._is_deleted = False
        self._updated_at = datetime.utcnow()

    def is_active(self) -> bool:
        return not self._is_deleted

    def is_owner(self, user_id: str) -> bool:
        return self._owner_id == str(user_id)

    def can_be_edited(self) -> bool:
        return self._status in [TripStatus.PLANNING.value, TripStatus.ACTIVE.value]

    def to_public_data(self) -> TripData:
        return TripData(
            id=self._id,
            title=self._title,
            description=self._description,
            destination=self._destination,
            start_date=self._start_date,
            end_date=self._end_date,
            owner_id=self._owner_id,
            category=self._category,
            status=self._status,
            is_group_trip=self._is_group_trip,
            is_public=self._is_public,
            budget_limit=self._budget_limit,
            currency=self._currency,
            image_url=self._image_url,
            notes=self._notes,
            total_expenses=self._total_expenses,
            member_count=self._member_count,
            created_at=self._created_at,
            updated_at=self._updated_at,
            is_deleted=self._is_deleted
        )

    @property
    def id(self) -> str:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @property
    def owner_id(self) -> str:
        return self._owner_id

    @property
    def status(self) -> str:
        return self._status

    @property
    def is_group_trip(self) -> bool:
        return self._is_group_trip

    @property
    def destination(self) -> str:
        return self._destination

    @property
    def start_date(self) -> datetime:
        return self._start_date

    @property
    def end_date(self) -> datetime:
        return self._end_date