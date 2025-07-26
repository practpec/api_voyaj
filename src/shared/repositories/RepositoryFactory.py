from typing import Dict, Any
from modules.users.infrastructure.repositories.UserMongoRepository import UserMongoRepository
from modules.friendships.infrastructure.repositories.friendship_mongo_repository import FriendshipMongoRepository
from modules.trips.infrastructure.repositories.trip_mongo_repository import TripMongoRepository
from modules.trips.infrastructure.repositories.trip_member_mongo_repository import TripMemberMongoRepository

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
    def clear_instances(cls):
        cls._instances.clear()