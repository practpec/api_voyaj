from typing import Dict, Any
from .AuthService import AuthService
from .EmailService import EmailService
from .UploadService import UploadService
from modules.friendships.domain.friendship_service import FriendshipService
from modules.trips.domain.trip_service import TripService
from modules.activities.domain.activity_service import ActivityService
from modules.diary_entries.domain.diary_entry_service import DiaryEntryService
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
    def get_friendship_service(cls) -> FriendshipService:
        if 'friendship' not in cls._instances:
            friendship_repo = RepositoryFactory.get_friendship_repository()
            cls._instances['friendship'] = FriendshipService(friendship_repo)
        return cls._instances['friendship']
    
    @classmethod
    def get_trip_service(cls) -> TripService:
        if 'trip' not in cls._instances:
            trip_repo = RepositoryFactory.get_trip_repository()
            trip_member_repo = RepositoryFactory.get_trip_member_repository()
            user_repo = RepositoryFactory.get_user_repository()
            cls._instances['trip'] = TripService(trip_repo, trip_member_repo, user_repo)
        return cls._instances['trip']
    
    @classmethod
    def get_activity_service(cls) -> ActivityService:
        if 'activity' not in cls._instances:
            activity_repo = RepositoryFactory.get_activity_repository()
            day_repo = RepositoryFactory.get_day_repository()
            trip_member_repo = RepositoryFactory.get_trip_member_repository()
            cls._instances['activity'] = ActivityService(
                activity_repository=activity_repo,
                day_repository=day_repo,
                trip_member_repository=trip_member_repo
            )
        return cls._instances['activity']
    
    @classmethod
    def get_diary_entry_service(cls) -> DiaryEntryService:
        if 'diary_entry' not in cls._instances:
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
    def clear_instances(cls):
        cls._instances.clear()