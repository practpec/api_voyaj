from typing import Dict, Any
from modules.users.infrastructure.repositories.UserMongoRepository import UserMongoRepository
from modules.friendships.infrastructure.repositories.friendship_mongo_repository import FriendshipMongoRepository
from modules.trips.infrastructure.repositories.trip_mongo_repository import TripMongoRepository
from modules.trips.infrastructure.repositories.trip_member_mongo_repository import TripMemberMongoRepository
from modules.days.infrastructure.repositories.day_mongo_repository import DayMongoRepository
from modules.activities.infrastructure.repositories.activity_mongo_repository import ActivityMongoRepository
from modules.diary_entries.infrastructure.repositories.diary_entry_mongo_repository import DiaryEntryMongoRepository
from modules.expenses.infrastructure.repositories.expense_mongo_repository import ExpenseMongoRepository
from modules.expense_splits.infrastructure.repositories.expense_split_mongo_repository import ExpenseSplitMongoRepository
from modules.photos.infrastructure.repositories.photo_mongo_repository import PhotoMongoRepository


class RepositoryFactory:
    _instances: Dict[str, Any] = {}
    
    @classmethod
    def get_user_repository(cls) -> UserMongoRepository:
        if 'user' not in cls._instances:
            cls._instances['user'] = UserMongoRepository()
        return cls._instances['user']
    
    @classmethod
    def get_friendship_repository(cls) -> FriendshipMongoRepository:
        if 'friendship' not in cls._instances:
            cls._instances['friendship'] = FriendshipMongoRepository()
        return cls._instances['friendship']
    
    @classmethod
    def get_trip_repository(cls) -> TripMongoRepository:
        if 'trip' not in cls._instances:
            cls._instances['trip'] = TripMongoRepository()
        return cls._instances['trip']
    
    @classmethod
    def get_trip_member_repository(cls) -> TripMemberMongoRepository:
        if 'trip_member' not in cls._instances:
            cls._instances['trip_member'] = TripMemberMongoRepository()
        return cls._instances['trip_member']
    
    @classmethod
    def get_day_repository(cls) -> DayMongoRepository:
        if 'day' not in cls._instances:
            cls._instances['day'] = DayMongoRepository()
        return cls._instances['day']
    
    @classmethod
    def get_activity_repository(cls) -> ActivityMongoRepository:
        if 'activity' not in cls._instances:
            cls._instances['activity'] = ActivityMongoRepository()
        return cls._instances['activity']
    
    @classmethod
    def get_diary_entry_repository(cls) -> DiaryEntryMongoRepository:
        if 'diary_entry' not in cls._instances:
            cls._instances['diary_entry'] = DiaryEntryMongoRepository()
        return cls._instances['diary_entry']
    
    @classmethod
    def get_expense_repository(cls) -> ExpenseMongoRepository:
        if 'expense' not in cls._instances:
            cls._instances['expense'] = ExpenseMongoRepository()
        return cls._instances['expense']
    
    @classmethod
    def get_expense_split_repository(cls) -> ExpenseSplitMongoRepository:
        if 'expense_split' not in cls._instances:
            cls._instances['expense_split'] = ExpenseSplitMongoRepository()
        return cls._instances['expense_split']
    
    @classmethod
    def get_photo_repository(cls) -> PhotoMongoRepository:
        if 'photo' not in cls._instances:
            cls._instances['photo'] = PhotoMongoRepository()
        return cls._instances['photo']
    
    @classmethod
    def clear_instances(cls):
        cls._instances.clear()