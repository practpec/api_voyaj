from typing import Dict, Any
from .AuthService import AuthService
from .EmailService import EmailService
from .UploadService import UploadService
from modules.friendships.domain.friendship_service import FriendshipService
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
    def clear_instances(cls):
        cls._instances.clear()