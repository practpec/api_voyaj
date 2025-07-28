# src/shared/services/ServiceFactory.py
from typing import Dict, Any
from .AuthService import AuthService
from .EmailService import EmailService
from .UploadService import UploadService
from shared.repositories.RepositoryFactory import RepositoryFactory


class ServiceFactory:
    _instances: Dict[str, Any] = {}
    
    @classmethod
    def get_auth_service(cls) -> AuthService:
        if 'auth' not in cls._instances:
            cls._instances['auth'] = AuthService()
        return cls._instances['auth']
    
    @classmethod
    def get_email_service(cls) -> EmailService:
        if 'email' not in cls._instances:
            cls._instances['email'] = EmailService()
        return cls._instances['email']
    
    @classmethod
    def get_upload_service(cls) -> UploadService:
        if 'upload' not in cls._instances:
            cls._instances['upload'] = UploadService()
        return cls._instances['upload']
    
    @classmethod
    def get_friendship_service(cls):
        """Obtener servicio de amistades"""
        if 'friendship' not in cls._instances:
            from modules.friendships.domain.friendship_service import FriendshipService
            
            friendship_repo = RepositoryFactory.get_friendship_repository()
            
            # FriendshipService solo necesita friendship_repository
            cls._instances['friendship'] = FriendshipService(
                friendship_repository=friendship_repo
            )
        return cls._instances['friendship']
    
    @classmethod
    def get_trip_service(cls):
        """Obtener servicio de viajes"""
        if 'trip' not in cls._instances:
            from modules.trips.domain.trip_service import TripService
            
            trip_repo = RepositoryFactory.get_trip_repository()
            trip_member_repo = RepositoryFactory.get_trip_member_repository()
            user_repo = RepositoryFactory.get_user_repository()
            
            cls._instances['trip'] = TripService(
                trip_repository=trip_repo,
                trip_member_repository=trip_member_repo,
                user_repository=user_repo
            )
        return cls._instances['trip']
    
    @classmethod
    def get_day_service(cls):
        """Obtener servicio de días"""
        if 'day' not in cls._instances:
            from modules.days.domain.day_service import DayService
            
            day_repo = RepositoryFactory.get_day_repository()
            trip_repo = RepositoryFactory.get_trip_repository()
            trip_member_repo = RepositoryFactory.get_trip_member_repository()
            
            cls._instances['day'] = DayService(
                day_repository=day_repo,
                trip_repository=trip_repo,
                trip_member_repository=trip_member_repo
            )
        return cls._instances['day']
    
    @classmethod
    def get_activity_service(cls):
        """Obtener servicio de actividades"""
        if 'activity' not in cls._instances:
            from modules.activities.domain.activity_service import ActivityService
            
            activity_repo = RepositoryFactory.get_activity_repository()
            day_repo = RepositoryFactory.get_day_repository()
            trip_repo = RepositoryFactory.get_trip_repository()
            trip_member_repo = RepositoryFactory.get_trip_member_repository()
            
            cls._instances['activity'] = ActivityService(
                activity_repository=activity_repo,
                day_repository=day_repo,
                trip_repository=trip_repo,
                trip_member_repository=trip_member_repo
            )
        return cls._instances['activity']
    
    @classmethod
    def get_diary_entry_service(cls):
        """Obtener servicio de entradas de diario"""
        if 'diary_entry' not in cls._instances:
            from modules.diary_entries.domain.diary_entry_service import DiaryEntryService
            
            diary_entry_repo = RepositoryFactory.get_diary_entry_repository()
            day_repo = RepositoryFactory.get_day_repository()
            trip_member_repo = RepositoryFactory.get_trip_member_repository()
            
            cls._instances['diary_entry'] = DiaryEntryService(
                diary_entry_repository=diary_entry_repo,
                day_repository=day_repo,
                trip_member_repository=trip_member_repo
            )
        return cls._instances['diary_entry']
    
    @classmethod
    def get_expense_service(cls):
        """Obtener servicio de gastos"""
        if 'expense' not in cls._instances:
            from modules.expenses.domain.expense_service import ExpenseService
            
            expense_repo = RepositoryFactory.get_expense_repository()
            trip_member_repo = RepositoryFactory.get_trip_member_repository()
            user_repo = RepositoryFactory.get_user_repository()
            trip_repo = RepositoryFactory.get_trip_repository()
            
            cls._instances['expense'] = ExpenseService(
                expense_repository=expense_repo,
                trip_member_repository=trip_member_repo,
                user_repository=user_repo,
                trip_repository=trip_repo
            )
        return cls._instances['expense']
    
    @classmethod
    def get_expense_split_service(cls):
        """Obtener servicio de divisiones de gastos"""
        if 'expense_split' not in cls._instances:
            from modules.expense_splits.domain.expense_split_service import ExpenseSplitService
            
            expense_split_repo = RepositoryFactory.get_expense_split_repository()
            expense_repo = RepositoryFactory.get_expense_repository()
            trip_member_repo = RepositoryFactory.get_trip_member_repository()
            
            cls._instances['expense_split'] = ExpenseSplitService(
                expense_split_repository=expense_split_repo,
                expense_repository=expense_repo,
                trip_member_repository=trip_member_repo
            )
        return cls._instances['expense_split']
    
    @classmethod
    def get_photo_service(cls):
        """Obtener servicio de fotos"""
        if 'photo' not in cls._instances:
            from modules.photos.domain.photo_service import PhotoService
            
            photo_repo = RepositoryFactory.get_photo_repository()
            trip_member_repo = RepositoryFactory.get_trip_member_repository()
            
            cls._instances['photo'] = PhotoService(
                photo_repository=photo_repo,
                trip_member_repository=trip_member_repo
            )
        return cls._instances['photo']
    
    @classmethod
    def get_activity_vote_service(cls):
        """Obtener servicio de votos de actividades"""
        if 'activity_vote' not in cls._instances:
            from modules.activity_votes.domain.activity_vote_service import ActivityVoteService
            
            activity_vote_repo = RepositoryFactory.get_activity_vote_repository()
            activity_repo = RepositoryFactory.get_activity_repository()
            trip_member_repo = RepositoryFactory.get_trip_member_repository()
            
            cls._instances['activity_vote'] = ActivityVoteService(
                activity_vote_repository=activity_vote_repo,
                activity_repository=activity_repo,
                trip_member_repository=trip_member_repo
            )
        return cls._instances['activity_vote']
    
    @classmethod
    def get_diary_recommendation_service(cls):
        """Obtener servicio de recomendaciones de diario"""
        if 'diary_recommendation' not in cls._instances:
            from modules.diary_recommendations.domain.diary_recommendation_service import DiaryRecommendationService
            
            recommendation_repo = RepositoryFactory.get_diary_recommendation_repository()
            diary_entry_repo = RepositoryFactory.get_diary_entry_repository()
            
            cls._instances['diary_recommendation'] = DiaryRecommendationService(
                recommendation_repository=recommendation_repo,
                diary_entry_repository=diary_entry_repo
            )
        return cls._instances['diary_recommendation']
    
    @classmethod
    def get_plan_reality_difference_service(cls):
        """Obtener servicio de diferencias plan vs realidad"""
        if 'plan_reality_difference' not in cls._instances:
            from modules.plan_reality_differences.domain.plan_reality_difference_service import PlanRealityDifferenceService
            
            plan_reality_difference_repo = RepositoryFactory.get_plan_reality_difference_repository()
            trip_member_repo = RepositoryFactory.get_trip_member_repository()
            
            cls._instances['plan_reality_difference'] = PlanRealityDifferenceService(
                plan_reality_difference_repository=plan_reality_difference_repo,
                trip_member_repository=trip_member_repo
            )
        return cls._instances['plan_reality_difference']