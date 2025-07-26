# src/modules/activity_votes/application/dtos/activity_vote_dto.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class CreateActivityVoteDTO(BaseModel):
    """DTO para crear voto de actividad"""
    vote_type: str = Field(..., description="Tipo de voto: up, down, neutral")

    class Config:
        str_strip_whitespace = True


class UpdateActivityVoteDTO(BaseModel):
    """DTO para actualizar voto de actividad"""
    vote_type: str = Field(..., description="Nuevo tipo de voto: up, down, neutral")

    class Config:
        str_strip_whitespace = True


class ActivityVoteResponseDTO(BaseModel):
    """DTO de respuesta para voto de actividad"""
    id: str
    activity_id: str
    user_id: str
    trip_id: str
    vote_type: str
    created_at: datetime
    updated_at: datetime
    user_info: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class ActivityVoteStatsDTO(BaseModel):
    """DTO para estadísticas de votos de actividad"""
    activity_id: str
    total_votes: int
    up_votes: int
    down_votes: int
    neutral_votes: int
    score: int
    popularity_percentage: float
    user_vote: Optional[str] = None

    class Config:
        from_attributes = True


class ActivityRankingDTO(BaseModel):
    """DTO para ranking de actividades"""
    activity_id: str
    activity_title: str
    activity_description: Optional[str]
    total_votes: int
    score: int
    ranking_position: int
    popularity_percentage: float

    class Config:
        from_attributes = True


class TripRankingsResponseDTO(BaseModel):
    """DTO de respuesta para rankings del viaje"""
    trip_id: str
    total_activities: int
    activities_with_votes: int
    rankings: List[ActivityRankingDTO]

    class Config:
        from_attributes = True


class TripPollsResponseDTO(BaseModel):
    """DTO de respuesta para encuestas del viaje"""
    trip_id: str
    active_polls: int
    polls: List[Dict[str, Any]]

    class Config:
        from_attributes = True


class UserVotesResponseDTO(BaseModel):
    """DTO de respuesta para votos del usuario"""
    user_id: str
    trip_id: Optional[str] = None
    total_votes: int
    votes: List[ActivityVoteResponseDTO]

    class Config:
        from_attributes = True


class ActivityVoteDTOMapper:
    """Mapper para convertir entre entidades y DTOs"""

    @staticmethod
    def to_activity_vote_response(
        vote_data: Any, 
        user_info: Optional[Dict[str, Any]] = None
    ) -> ActivityVoteResponseDTO:
        """Convertir datos de voto a DTO de respuesta"""
        return ActivityVoteResponseDTO(
            id=vote_data.id,
            activity_id=vote_data.activity_id,
            user_id=vote_data.user_id,
            trip_id=vote_data.trip_id,
            vote_type=vote_data.vote_type,
            created_at=vote_data.created_at,
            updated_at=vote_data.updated_at,
            user_info=user_info
        )

    @staticmethod
    def to_activity_vote_stats(
        stats_data: Dict[str, Any], 
        user_vote: Optional[str] = None
    ) -> ActivityVoteStatsDTO:
        """Convertir estadísticas a DTO"""
        return ActivityVoteStatsDTO(
            activity_id=stats_data['activity_id'],
            total_votes=stats_data['total_votes'],
            up_votes=stats_data['up_votes'],
            down_votes=stats_data['down_votes'],
            neutral_votes=stats_data['neutral_votes'],
            score=stats_data['score'],
            popularity_percentage=stats_data['popularity_percentage'],
            user_vote=user_vote
        )

    @staticmethod
    def to_activity_ranking(ranking_data: Dict[str, Any]) -> ActivityRankingDTO:
        """Convertir datos de ranking a DTO"""
        return ActivityRankingDTO(
            activity_id=ranking_data['activity_id'],
            activity_title=ranking_data['activity_title'],
            activity_description=ranking_data.get('activity_description'),
            total_votes=ranking_data['total_votes'],
            score=ranking_data['score'],
            ranking_position=ranking_data['ranking_position'],
            popularity_percentage=ranking_data['popularity_percentage']
        )

    @staticmethod
    def to_trip_rankings_response(
        trip_id: str, 
        rankings_data: List[Dict[str, Any]]
    ) -> TripRankingsResponseDTO:
        """Convertir rankings del viaje a DTO de respuesta"""
        rankings = [
            ActivityVoteDTOMapper.to_activity_ranking(ranking) 
            for ranking in rankings_data
        ]
        
        return TripRankingsResponseDTO(
            trip_id=trip_id,
            total_activities=len(rankings_data),
            activities_with_votes=sum(1 for r in rankings_data if r['total_votes'] > 0),
            rankings=rankings
        )

    @staticmethod
    def to_user_votes_response(
        user_id: str, 
        votes_data: List[Any], 
        trip_id: Optional[str] = None
    ) -> UserVotesResponseDTO:
        """Convertir votos del usuario a DTO de respuesta"""
        votes = [
            ActivityVoteDTOMapper.to_activity_vote_response(vote) 
            for vote in votes_data
        ]
        
        return UserVotesResponseDTO(
            user_id=user_id,
            trip_id=trip_id,
            total_votes=len(votes),
            votes=votes
        )