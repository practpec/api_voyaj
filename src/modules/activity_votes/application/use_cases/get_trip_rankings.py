# src/modules/activity_votes/application/use_cases/get_trip_rankings.py
from ..dtos.activity_vote_dto import TripRankingsResponseDTO, ActivityVoteDTOMapper
from ...domain.activity_vote_service import ActivityVoteService


class GetTripRankingsUseCase:
    def __init__(self, activity_vote_service: ActivityVoteService):
        self._activity_vote_service = activity_vote_service

    async def execute(self, trip_id: str, user_id: str) -> TripRankingsResponseDTO:
        """Obtener ranking de actividades del viaje por votos"""
        rankings_data = await self._activity_vote_service.get_trip_activity_rankings(
            trip_id, user_id
        )

        return ActivityVoteDTOMapper.to_trip_rankings_response(trip_id, rankings_data)