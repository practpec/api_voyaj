# src/shared/repositories/RepositoryFactory.py
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
from modules.activity_votes.infrastructure.repositories.activity_vote_mongo_repository import ActivityVoteMongoRepository
from modules.diary_recommendations.infrastructure.repositories.diary_recommendation_mongo_repository import DiaryRecommendationMongoRepository
from modules.plan_reality_differences.infrastructure.repositories.plan_reality_difference_mongo_repository import PlanRealityDifferenceMongoRepository


class RepositoryFactory:
    _instances: Dict[str, Any] = {}
    
    @classmethod
    def get_user_repository(cls) -> UserMongoRepository:
        if 'user' not in cls._instances:
            cls._instances['user'] = UserMongoRepository()
        return cls._instances['user']

    @classmethod
    def get_friendship_repository(cls):
        """Obtener repositorio de amistades"""
        if 'friendship' not in cls._instances:
            from modules.friendships.infrastructure.repositories.friendship_mongo_repository import FriendshipMongoRepository
            cls._instances['friendship'] = FriendshipMongoRepository()
        return cls._instances['friendship']
    
    @classmethod
    def get_trip_repository(cls):
        """Obtener repositorio de viajes"""
        if 'trip' not in cls._instances:
            from modules.trips.infrastructure.repositories.trip_mongo_repository import TripMongoRepository
            cls._instances['trip'] = TripMongoRepository()
        return cls._instances['trip']
    
    @classmethod
    def get_trip_member_repository(cls):
        """Obtener repositorio de miembros de viaje"""
        if 'trip_member' not in cls._instances:
            from modules.trips.infrastructure.repositories.trip_member_mongo_repository import TripMemberMongoRepository
            cls._instances['trip_member'] = TripMemberMongoRepository()
        return cls._instances['trip_member']
    
    @classmethod
    def get_day_repository(cls) -> DayMongoRepository:
        if 'day' not in cls._instances:
            from modules.days.infrastructure.repositories.day_mongo_repository import DayMongoRepository
            cls._instances['day'] = DayMongoRepository()
        return cls._instances['day']
    
    @classmethod
    def get_activity_repository(cls) -> ActivityMongoRepository:
        if 'activity' not in cls._instances:
            from modules.activities.infrastructure.repositories.activity_mongo_repository import ActivityMongoRepository
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
    def get_activity_vote_repository(cls) -> ActivityVoteMongoRepository:
        if 'activity_vote' not in cls._instances:
            cls._instances['activity_vote'] = ActivityVoteMongoRepository()
        return cls._instances['activity_vote']
    
    @classmethod
    def get_diary_recommendation_repository(cls) -> DiaryRecommendationMongoRepository:
        if 'diary_recommendation' not in cls._instances:
            cls._instances['diary_recommendation'] = DiaryRecommendationMongoRepository()
        return cls._instances['diary_recommendation']
    
    @classmethod
    def get_plan_reality_difference_repository(cls):
        """Obtener repositorio de diferencias plan vs realidad"""
        if 'plan_reality_difference' not in cls._instances:
            from modules.plan_reality_differences.infrastructure.repositories.plan_reality_difference_mongo_repository import PlanRealityDifferenceMongoRepository
            cls._instances['plan_reality_difference'] = PlanRealityDifferenceMongoRepository()
        return cls._instances['plan_reality_difference']