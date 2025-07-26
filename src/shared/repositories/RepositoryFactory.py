from typing import Dict, Any, Type
from modules.users.infrastructure.repositories.UserMongoRepository import UserMongoRepository
from modules.friendships.infrastructure.repositories.friendship_mongo_repository import FriendshipMongoRepository

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
    def clear_instances(cls):
        cls._instances.clear()